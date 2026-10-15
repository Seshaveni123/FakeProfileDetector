"""Regression tests for the Twitter training/artifact contract."""
import importlib.util
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_trainer():
    spec = importlib.util.spec_from_file_location("fakeguard_trainer", ROOT / "ml" / "train_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_prediction_app(monkeypatch):
    monkeypatch.setenv("MODEL_DIR", str(ROOT / "backend" / "models"))
    sys.path.insert(0, str(ROOT / "services" / "prediction-service"))
    sys.modules.pop("app", None)
    import app
    return app


def test_twitter_dataset_label_and_feature_mapping():
    trainer = load_trainer()
    raw = pd.read_csv(ROOT / "twitter1" / "bot_detection_data.csv")
    frame = trainer.validate_twitter_frame(raw)
    assert set(frame["is_fake"].unique()) == {0, 1}
    assert list(frame[trainer.TWITTER_FEATURE_COLUMNS].columns) == trainer.TWITTER_FEATURE_COLUMNS
    assert set(frame["Verified"].unique()) <= {0, 1}


def test_metrics_use_positive_bot_class_and_predictions():
    trainer = load_trainer()
    metrics = trainer.metrics_from_predictions(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 0]), np.array([0.1, 0.8, 0.9, 0.2]))
    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert metrics["accuracy"] == 0.5
    assert metrics["auc_roc"] == 0.75


def test_twitter_artifacts_and_metadata_share_schema():
    with open(ROOT / "backend" / "models" / "twitter_model.pkl", "rb") as handle:
        model = pickle.load(handle)
    metadata = json.loads((ROOT / "backend" / "models" / "twitter_metadata.json").read_text(encoding="utf-8"))
    assert metadata["feature_columns"] == ["Retweet Count", "Mention Count", "Follower Count", "Verified"]
    assert model.n_features_in_ == len(metadata["feature_columns"])
    assert metadata["training_samples"] + metadata["test_samples"] == metadata["total_samples"]
    assert metadata["evaluation"]["positive_class"] == 1
    assert {"Random Forest", "XGBoost"} <= set(metadata["results"])
    assert metadata["best_model"] in metadata["results"]


def test_prediction_service_reports_loaded_twitter_artifact(monkeypatch):
    prediction_app = load_prediction_app(monkeypatch)
    info = prediction_app.model_info("twitter")["twitter"]
    result = prediction_app.classify(prediction_app.PredictionRequest(platform="twitter", retweet_count=10, mention_count=1, follower_count_twitter=1000, verified=0))
    assert info["model_name"] == prediction_app.twitter_metadata["best_model"]
    assert info["feature_columns"] == prediction_app.twitter_metadata["feature_columns"]
    assert info["training_results"] == prediction_app.twitter_metadata["results"]
    assert info["quality"] == prediction_app.twitter_metadata["quality"]
    assert result["is_fake"] in {0, 1}
    assert 0.0 <= result["probability"] <= 1.0


def test_instagram_artifact_remains_loadable(monkeypatch):
    prediction_app = load_prediction_app(monkeypatch)
    result = prediction_app.classify(prediction_app.PredictionRequest(platform="instagram"))
    assert result["platform"] == "instagram"
    assert result["is_fake"] in {0, 1}
    assert 0.0 <= result["probability"] <= 1.0
