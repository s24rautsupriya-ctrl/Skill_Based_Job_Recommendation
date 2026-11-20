# Skill-Based Job Recommendation System

Beginner-friendly college mini-project using Python, Flask, scikit-learn, HTML/CSS/JavaScript and MySQL.

## Included features
- Register/login with hashed passwords
- Student profile: education, experience, skills and interests
- Top-five job-category recommendations using TF-IDF + cosine similarity
- Matched and missing skills display
- MySQL recommendation history
- Optional `.txt` resume skill extraction
- Sample dataset with 30 job profiles

**Important:** Match percentages are text-similarity scores against this sample dataset. They are not probabilities of being hired or guarantees of suitability.

## Setup (Windows + VS Code)
1. Install Python 3.10+ and MySQL Server.
2. Open `database/database.sql` in MySQL Workbench and execute it.
3. Copy `.env.example` to a new file named `.env`. Enter your MySQL username/password. Keep `.env` private.
4. Open this folder in VS Code > Terminal > New Terminal.
5. Run:

```powershell
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
python app.py
```

6. Open `http://127.0.0.1:5000`.
7. Register, log in, complete My Profile, then choose Recommendations.

If `py` is not recognized, use `python` instead.

## Database tables
`users`, `user_profiles`, `jobs`, `recommendations`.

## Dataset
The included `dataset/jobs.csv` is a small hand-prepared educational sample. To expand it, see:
- O*NET: https://www.onetcenter.org/database.html
- ESCO: https://esco.ec.europa.eu/en/use-esco/download

Check dataset licences/terms before redistributing external data.

## Troubleshooting
- MySQL connection error: check that MySQL Server is running and `.env` matches your local MySQL credentials.
- Unknown database: run `database/database.sql`.
- Flask module missing: activate `venv` and run `pip install -r requirements.txt`.
- Port busy: change `app.run(debug=True)` to `app.run(debug=True, port=5001)`.

Resume extraction in this starter version accepts `.txt` files only. The system is an educational prototype; users should review recommendations themselves.
