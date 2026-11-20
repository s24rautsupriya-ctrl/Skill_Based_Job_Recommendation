
import os
from functools import wraps

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from recommender import recommend_jobs, extract_resume_skills


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key-for-local-development"
)

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# --------------------------------------------------
# 2. MYSQL DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv(
            "DB_NAME",
            "job_recommendation_system"
        ),
        autocommit=False
    )


# --------------------------------------------------
# 3. DATABASE HELPER
# --------------------------------------------------

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id, name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# 4. LOGIN REQUIRED DECORATOR
# --------------------------------------------------

def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# 5. HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# 6. USER REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))

        if len(name) > 100 or len(email) > 150:
            flash("Name or email is too long.", "danger")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("register"))

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check whether email already exists
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                flash(
                    "This email is already registered. Please login.",
                    "warning"
                )
                return redirect(url_for("login"))

            hashed_password = generate_password_hash(password)

            # IMPORTANT: actual primary key is user_id.
            # MySQL generates user_id automatically.
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            conn.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except Error:
            if conn:
                conn.rollback()

            app.logger.exception("Registration database error")
            flash(
                "Registration could not be completed. "
                "Please check the database configuration.",
                "danger"
            )

        finally:
            if cursor:
                cursor.close()

            if conn and conn.is_connected():
                conn.close()

    return render_template("register.html")


# --------------------------------------------------
# 7. USER LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Enter your email and password.", "danger")
            return redirect(url_for("login"))

        try:
            user = get_user_by_email(email)

            if user and check_password_hash(
                user["password_hash"],
                password
            ):

                session.clear()

                # Store the correct database primary key
                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                session["email"] = user["email"]

                flash("Welcome back!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "danger")

        except Error:
            app.logger.exception("Login database error")
            flash("Unable to connect to the database.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# 8. LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "info")

    return redirect(url_for("index"))


# --------------------------------------------------
# 9. DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS total_jobs
            FROM jobs
            """
        )
        job_count = cursor.fetchone()["total_jobs"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total_recommendations
            FROM recommendations
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )
        recommendation_count = cursor.fetchone()["total_recommendations"]

        return render_template(
            "dashboard.html",
            job_count=job_count,
            recommendation_count=recommendation_count
        )

    except Error:
        app.logger.exception("Dashboard database error")
        flash("Unable to load dashboard data.", "danger")

        return render_template(
            "dashboard.html",
            job_count=0,
            recommendation_count=0
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# --------------------------------------------------
# 10. USER PROFILE
# --------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    user_id = session["user_id"]

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":

            skills = request.form.get("skills", "").strip()
            education = request.form.get("education", "").strip()
            interests = request.form.get("interests", "").strip()
            experience = request.form.get("experience", "").strip()

            cursor.execute(
                """
                INSERT INTO user_profiles
                    (user_id, skills, education, interests, experience)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    skills = VALUES(skills),
                    education = VALUES(education),
                    interests = VALUES(interests),
                    experience = VALUES(experience)
                """,
                (user_id, skills, education, interests, experience)
            )

            conn.commit()

            flash("Profile updated successfully.", "success")

        cursor.execute(
            """
            SELECT *
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

        profile_data = cursor.fetchone()

        return render_template(
            "profile.html",
            profile=profile_data
        )

    except Error:
        if conn:
            conn.rollback()

        app.logger.exception("Profile database error")
        flash("Unable to save or load your profile.", "danger")

        return render_template(
            "profile.html",
            profile=None
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# --------------------------------------------------
# 11. JOB RECOMMENDATIONS
# --------------------------------------------------

@app.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():

    recommendations_list = []

    if request.method == "POST":

        skills = request.form.get("skills", "").strip()

        if not skills:
            flash("Please enter your skills.", "warning")
            return render_template(
                "recommend.html",
                recommendations=recommendations_list
            )

        try:
            # TF-IDF and cosine similarity recommendation
            recommendations_list = recommend_jobs(skills)

            # Save recommendation history
            conn = get_db_connection()
            cursor = conn.cursor()

            for job in recommendations_list:

                job_id = job.get("job_id", job.get("id"))
                score = job.get("score", 0)

                if job_id is not None:
                    cursor.execute(
                        """
                        INSERT INTO recommendations
                            (user_id, job_id, match_score)
                        VALUES (%s, %s, %s)
                        """,
                        (session["user_id"], job_id, score)
                    )

            conn.commit()

        except Error:
            if "conn" in locals():
                conn.rollback()

            app.logger.exception("Recommendation database error")
            flash("Could not save recommendation history.", "danger")

        except Exception:
            app.logger.exception("Recommendation engine error")
            flash("Unable to generate recommendations.", "danger")

        finally:
            if "cursor" in locals():
                cursor.close()

            if "conn" in locals() and conn.is_connected():
                conn.close()

    return render_template(
        "recommend.html",
        recommendations=recommendations_list
    )


# --------------------------------------------------
# 12. RECOMMENDATION HISTORY
# --------------------------------------------------

@app.route("/history")
@login_required
def history():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                r.*,
                j.title,
                j.company,
                j.location
            FROM recommendations r
            JOIN jobs j ON r.job_id = j.job_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (session["user_id"],)
        )

        history_data = cursor.fetchall()

        return render_template(
            "history.html",
            history=history_data
        )

    except Error:
        app.logger.exception("History database error")
        flash("Unable to load recommendation history.", "danger")

        return render_template(
            "history.html",
            history=[]
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# --------------------------------------------------
# 13. RESUME SKILL EXTRACTION
# --------------------------------------------------

@app.route("/resume-skills", methods=["GET", "POST"])
@login_required
def resume_skills():

    extracted_skills = []

    if request.method == "POST":

        resume = request.files.get("resume")

        if not resume or not resume.filename:
            flash("Please select a resume text file.", "warning")

            return render_template(
                "resume_skills.html",
                skills=extracted_skills
            )

        filename = secure_filename(resume.filename)

        if not filename.lower().endswith(".txt"):
            flash("Please upload a .txt resume file.", "danger")

            return render_template(
                "resume_skills.html",
                skills=extracted_skills
            )

        try:
            resume_text = resume.read().decode(
                "utf-8",
                errors="ignore"
            )

            extracted_skills = extract_resume_skills(resume_text)

            flash("Resume skills extracted successfully.", "success")

        except Exception:
            app.logger.exception("Resume extraction error")
            flash("Unable to extract resume skills.", "danger")

    return render_template(
        "resume_skills.html",
        skills=extracted_skills
    )


# --------------------------------------------------
# 14. DATABASE HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():

    conn = None

    try:
        conn = get_db_connection()

        if conn.is_connected():
            return {
                "status": "ok",
                "message": "Database connected successfully"
            }, 200

        return {
            "status": "error",
            "message": "Database connection is not active"
        }, 500

    except Error:
        app.logger.exception("Health check failed")

        return {
            "status": "error",
            "message": "Database connection failed. Check .env and MySQL."
        }, 500

    finally:
        if conn and conn.is_connected():
            conn.close()


# --------------------------------------------------
# 15. APPLICATION START
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
