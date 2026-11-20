# Optional preparation script: verifies the dataset and saves the TF-IDF model.
import pickle
from recommender import load_jobs
from sklearn.feature_extraction.text import TfidfVectorizer
jobs=load_jobs()
docs=[" ".join([j["required_skills"],j["title"],j["category"],j["education"]]) for j in jobs]
vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2))
matrix=vectorizer.fit_transform(docs)
with open("model.pkl","wb") as f: pickle.dump({"vectorizer":vectorizer,"matrix":matrix,"titles":[j["title"] for j in jobs]},f)
print(f"Prepared model using {len(jobs)} job profiles. Saved model.pkl")
