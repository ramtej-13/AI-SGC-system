import os
import json
import joblib
import numpy as np
from typing import Dict, Any, List, Optional
from app.ml.preprocessing import clean_text

class GrievanceClassifier:
    DEFAULT_THRESHOLD = 0.70
    FALLBACK_CATEGORY = "Other / Manual Review"

    def __init__(self, artifacts_dir: Optional[str] = None):
        if not artifacts_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            artifacts_dir = os.path.join(base_dir, "artifacts")
            
        self.artifacts_dir = artifacts_dir
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.metadata = None
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = os.path.join(self.artifacts_dir, "model.joblib")
        vectorizer_path = os.path.join(self.artifacts_dir, "vectorizer.joblib")
        le_path = os.path.join(self.artifacts_dir, "label_encoder.joblib")
        meta_path = os.path.join(self.artifacts_dir, "metadata.json")

        if (os.path.exists(model_path) and os.path.exists(vectorizer_path) 
                and os.path.exists(le_path)):
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.label_encoder = joblib.load(le_path)
            
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.vectorizer is not None and self.label_encoder is not None

    def predict(self, raw_text: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Classifies input grievance text and returns predicted category, confidence,
        and top-3 class probabilities for explainability.
        """
        applied_threshold = threshold if threshold is not None else self.DEFAULT_THRESHOLD

        if not self.is_ready:
            # Fallback if model is not yet trained
            return {
                "predicted_category": self.FALLBACK_CATEGORY,
                "confidence": 0.0,
                "is_low_confidence": True,
                "top_predictions": [{"category": self.FALLBACK_CATEGORY, "probability": 0.0}],
                "raw_predicted_category": self.FALLBACK_CATEGORY,
                "raw_confidence": 0.0,
                "threshold_applied": applied_threshold,
                "cleaned_text": clean_text(raw_text)
            }

        cleaned = clean_text(raw_text)
        if not cleaned:
            return {
                "predicted_category": self.FALLBACK_CATEGORY,
                "confidence": 0.0,
                "is_low_confidence": True,
                "top_predictions": [{"category": self.FALLBACK_CATEGORY, "probability": 0.0}],
                "raw_predicted_category": self.FALLBACK_CATEGORY,
                "raw_confidence": 0.0,
                "threshold_applied": applied_threshold,
                "cleaned_text": ""
            }

        X_vec = self.vectorizer.transform([cleaned])
        probas = self.model.predict_proba(X_vec)[0]
        classes = self.label_encoder.classes_

        # Sort classes by probability descending
        sorted_indices = np.argsort(probas)[::-1]
        top_indices = sorted_indices[:3]

        top_predictions: List[Dict[str, Any]] = [
            {
                "category": str(classes[idx]),
                "probability": round(float(probas[idx]), 4)
            }
            for idx in top_indices
        ]

        raw_top_category = str(classes[sorted_indices[0]])
        raw_confidence = round(float(probas[sorted_indices[0]]), 4)

        # Apply confidence threshold fallback
        is_low_confidence = raw_confidence < applied_threshold
        if is_low_confidence:
            final_category = self.FALLBACK_CATEGORY
        else:
            final_category = raw_top_category

        return {
            "predicted_category": final_category,
            "confidence": raw_confidence,
            "is_low_confidence": is_low_confidence,
            "top_predictions": top_predictions,
            "raw_predicted_category": raw_top_category,
            "raw_confidence": raw_confidence,
            "threshold_applied": applied_threshold,
            "cleaned_text": cleaned
        }

# Global singleton instance
_classifier_instance: Optional[GrievanceClassifier] = None

def get_classifier() -> GrievanceClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = GrievanceClassifier()
    return _classifier_instance
