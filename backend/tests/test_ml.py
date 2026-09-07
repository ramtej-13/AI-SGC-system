import pytest
from app.ml.preprocessing import clean_text
from app.ml.predict import get_classifier

def test_clean_text_normal():
    raw = "The Wi-Fi in CS Lab 2 is NOT working!! Check https://example.com"
    cleaned = clean_text(raw)
    assert "https" not in cleaned
    assert "!" not in cleaned
    assert "wi fi" in cleaned or "wifi" in cleaned
    assert "cs lab 2" in cleaned

def test_clean_text_edge_cases():
    assert clean_text("") == ""
    assert clean_text(None) == ""
    assert clean_text("   \n\t   ") == ""
    assert clean_text("Email: test@college.edu") == "email"

def test_classifier_is_ready():
    classifier = get_classifier()
    assert classifier.is_ready is True
    assert classifier.metadata is not None
    assert "accuracy" in classifier.metadata["evaluation_metrics"]

def test_classifier_prediction_structure():
    classifier = get_classifier()
    sample = "The Ethernet LAN port and Wi-Fi connection in computer center are completely disconnected."
    res = classifier.predict(sample)

    assert "predicted_category" in res
    assert "confidence" in res
    assert "is_low_confidence" in res
    assert "top_predictions" in res
    assert len(res["top_predictions"]) == 3
    assert res["predicted_category"] == "IT / Network"
    assert res["is_low_confidence"] is False

def test_classifier_threshold_fallback():
    classifier = get_classifier()
    # Ambiguous or out-of-domain text with high threshold to trigger fallback
    sample = "Hello sir, I have a general query."
    res = classifier.predict(sample, threshold=0.999)

    assert res["is_low_confidence"] is True
    assert res["predicted_category"] == "Other / Manual Review"
    assert res["threshold_applied"] == 0.999

def test_classifier_top_3_probabilities():
    classifier = get_classifier()
    sample = "Power cut in classroom and switchboard is smelling burnt."
    res = classifier.predict(sample)
    top = res["top_predictions"]
    assert len(top) == 3
    # Verify probabilities are sorted descending
    assert top[0]["probability"] >= top[1]["probability"] >= top[2]["probability"]
