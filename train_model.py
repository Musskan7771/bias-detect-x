import os
import json
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "bias_dataset.csv")
MODEL = os.path.join(BASE, "model", "bias_model.pkl")
METRICS = os.path.join(BASE, "model", "model_metrics.json")

df = pd.read_csv(DATA)
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.20, random_state=42, stratify=df["label"]
)

def make_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1
        )),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))
    ])

# Holdout evaluation for honest performance reporting.
eval_model = make_pipeline()
eval_model.fit(X_train, y_train)
pred = eval_model.predict(X_test)
classes = sorted(df["label"].unique())
cm = confusion_matrix(y_test, pred, labels=classes)

metrics = {
    "total_examples": int(len(df)),
    "examples_per_category": int(df["label"].value_counts().min()),
    "categories": len(classes),
    "train_examples": int(len(X_train)),
    "test_examples": int(len(X_test)),
    "accuracy": round(float(accuracy_score(y_test, pred)) * 100, 2),
    "precision": round(float(precision_score(y_test, pred, average="weighted", zero_division=0)) * 100, 2),
    "recall": round(float(recall_score(y_test, pred, average="weighted", zero_division=0)) * 100, 2),
    "f1": round(float(f1_score(y_test, pred, average="weighted", zero_division=0)) * 100, 2),
    "labels": classes,
    "confusion_matrix": cm.tolist(),
}

# Final model trained on all 1,600 examples for the website.
final_model = make_pipeline()
final_model.fit(df["text"], df["label"])
joblib.dump(final_model, MODEL)
with open(METRICS, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"Model trained on {len(df)} examples.")
print(f"Saved to: {MODEL}")
print(f"Saved metrics to: {METRICS}")
print(f"Holdout accuracy: {metrics['accuracy']}%")
print("Classes:", classes)
