
import os
import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# 1. DATASET LOCATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "jobs.csv"
)


# --------------------------------------------------
# 2. LOAD JOB DATASET
# --------------------------------------------------

def load_jobs():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            "jobs.csv not found inside the dataset folder."
        )

    df = pd.read_csv(DATASET_PATH)

    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["title", "description"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing required dataset column: {column}"
            )

    # Add optional columns if they do not exist
    optional_columns = [
        "category",
        "skills",
        "company",
        "location"
    ]

    for column in optional_columns:
        if column not in df.columns:
            df[column] = ""

    # Use an existing job identifier when available
    if "job_id" not in df.columns:
        if "id" in df.columns:
            df["job_id"] = df["id"]
        else:
            df["job_id"] = range(1, len(df) + 1)

    df = df.fillna("")

    return df


# --------------------------------------------------
# 3. CLEAN TEXT
# --------------------------------------------------

def clean_text(text):

    text = str(text).lower()

    text = re.sub(r"[^a-z0-9+#. ]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# 4. SPLIT SKILLS
# --------------------------------------------------

def split_skills(text):

    if not text:
        return []

    skills = re.split(r"[,;\n|]", str(text))

    return [
        clean_text(skill)
        for skill in skills
        if clean_text(skill)
    ]


# --------------------------------------------------
# 5. GENERATE JOB RECOMMENDATIONS
# --------------------------------------------------

def recommend_jobs(user_input, top_n=5):

    if not str(user_input).strip():
        return []

    jobs = load_jobs()

    if jobs.empty:
        return []

    # Combine job information for text similarity
    job_documents = (
        jobs["title"].astype(str) + " " +
        jobs["category"].astype(str) + " " +
        jobs["description"].astype(str) + " " +
        jobs["skills"].astype(str)
    ).apply(clean_text)

    user_text = clean_text(user_input)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    documents = job_documents.tolist() + [user_text]

    tfidf_matrix = vectorizer.fit_transform(documents)

    # Cosine similarity
    similarity_scores = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    ).flatten()

    # Find the best matching jobs
    ranked_indices = similarity_scores.argsort()[::-1]

    results = []

    user_skills = split_skills(user_input)

    for index in ranked_indices[:top_n]:

        job = jobs.iloc[index]

        job_skills = split_skills(job["skills"])

        matched = [
            skill for skill in job_skills
            if skill in user_skills
        ]

        missing = [
            skill for skill in job_skills
            if skill not in user_skills
        ]

        score = round(
            float(similarity_scores[index]) * 100,
            2
        )

        results.append({

            "job_id": int(job["job_id"]),

            "title": str(job["title"]),

            "category": str(job["category"]),

            "description": str(job["description"]),

            "company": str(job["company"]),

            "location": str(job["location"]),

            "score": score,

            "matched": matched,

            "missing": missing

        })

    return results


# --------------------------------------------------
# 6. RESUME SKILL EXTRACTION
# --------------------------------------------------

def extract_resume_skills(resume_text):

    jobs = load_jobs()

    all_skills = []

    for skill_text in jobs["skills"]:

        all_skills.extend(split_skills(skill_text))

    unique_skills = list(set(all_skills))

    resume_text = clean_text(resume_text)

    extracted_skills = []

    for skill in unique_skills:

        if skill and re.search(
            r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
            resume_text
        ):
            extracted_skills.append(skill)

    return sorted(extracted_skills)
