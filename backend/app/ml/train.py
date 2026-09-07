import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from app.ml.preprocessing import clean_text

def train_model(data_path: str = None, artifacts_dir: str = None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not data_path:
        data_path = os.path.join(os.path.dirname(base_dir), "data", "grievances.csv")
    if not artifacts_dir:
        artifacts_dir = os.path.join(base_dir, "artifacts")
        
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print(f"[*] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"[*] Total records loaded: {len(df)}")
    
    # Preprocess texts
    df["cleaned_text"] = df["text"].apply(clean_text)
    
    # Filter empty texts if any
    df = df[df["cleaned_text"].str.strip() != ""].reset_index(drop=True)
    
    X = df["cleaned_text"].values
    y_raw = df["category"].values
    
    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    categories = list(label_encoder.classes_)
    print(f"[*] Categories ({len(categories)}): {categories}")
    
    # Stratified Train/Test Split (80/20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Fit TF-IDF Vectorizer ONLY on train set to prevent data leakage
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"[*] TF-IDF feature vocabulary size: {X_train_vec.shape[1]}")
    
    # Candidate models for academic comparison
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
            C=12.0
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Linear SVC": CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", random_state=42, max_iter=2000),
            cv=3
        )
    }
    
    comparison_results = {}
    best_model_name = "Logistic Regression"
    best_f1 = -1.0
    trained_models = {}
    
    for name, model in models.items():
        print(f"[*] Training candidate: {name}...")
        model.fit(X_train_vec, y_train)
        preds = model.predict(X_test_vec)
        
        acc = float(accuracy_score(y_test, preds))
        macro_prec = float(precision_score(y_test, preds, average="macro", zero_division=0))
        macro_rec = float(recall_score(y_test, preds, average="macro", zero_division=0))
        macro_f1 = float(f1_score(y_test, preds, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_test, preds, average="weighted", zero_division=0))
        
        comparison_results[name] = {
            "accuracy": round(acc, 4),
            "macro_precision": round(macro_prec, 4),
            "macro_recall": round(macro_rec, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4)
        }
        trained_models[name] = model
        print(f"    -> Acc: {acc:.4f}, Macro F1: {macro_f1:.4f}, Weighted F1: {weighted_f1:.4f}")
        
        if macro_f1 > best_f1:
            best_f1 = macro_f1
            best_model_name = name
            
    selected_model = trained_models["Logistic Regression"]
    test_preds = selected_model.predict(X_test_vec)
    
    cm = confusion_matrix(y_test, test_preds)
    cm_list = cm.tolist()
    
    rep = classification_report(y_test, test_preds, target_names=categories, output_dict=True, zero_division=0)
    
    metadata = {
        "training_timestamp": datetime.utcnow().isoformat(),
        "total_samples": int(len(df)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "vocabulary_size": int(X_train_vec.shape[1]),
        "categories": categories,
        "model_architecture": "TF-IDF (unigrams + bigrams) + Multinomial Logistic Regression",
        "default_confidence_threshold": 0.70,
        "comparison_benchmarks": comparison_results,
        "selected_model": "Logistic Regression",
        "evaluation_metrics": {
            "accuracy": round(float(accuracy_score(y_test, test_preds)), 4),
            "macro_precision": round(float(precision_score(y_test, test_preds, average="macro", zero_division=0)), 4),
            "macro_recall": round(float(recall_score(y_test, test_preds, average="macro", zero_division=0)), 4),
            "macro_f1": round(float(f1_score(y_test, test_preds, average="macro", zero_division=0)), 4),
            "weighted_f1": round(float(f1_score(y_test, test_preds, average="weighted", zero_division=0)), 4)
        },
        "per_class_metrics": {cat: rep[cat] for cat in categories if cat in rep},
        "confusion_matrix": {
            "matrix": cm_list,
            "labels": categories
        }
    }
    
    # Save artifacts
    model_path = os.path.join(artifacts_dir, "model.joblib")
    vectorizer_path = os.path.join(artifacts_dir, "vectorizer.joblib")
    le_path = os.path.join(artifacts_dir, "label_encoder.joblib")
    meta_path = os.path.join(artifacts_dir, "metadata.json")
    
    joblib.dump(selected_model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(label_encoder, le_path)
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"[+] Successfully saved artifacts to {artifacts_dir}")
    return metadata

if __name__ == "__main__":
    train_model()
