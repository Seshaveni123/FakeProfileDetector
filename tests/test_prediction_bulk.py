"""Bulk CSV behavior for the prediction service without external services."""
import asyncio
import io
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from test_twitter_pipeline import load_prediction_app

ROOT = Path(__file__).resolve().parents[1]


def upload(name, content):
    return UploadFile(filename=name, file=io.BytesIO(content.encode("utf-8")))


@pytest.mark.parametrize("platform,payload", [
    ("instagram", {"followers_count": 3200, "following_count": 420, "posts_count": 100}),
    ("twitter", {"retweet_count": 8, "mention_count": 1, "follower_count_twitter": 3000, "verified": 1}),
])
def test_single_prediction_endpoint_uses_loaded_model(monkeypatch, platform, payload):
    app = load_prediction_app(monkeypatch)
    monkeypatch.setattr(app, "persist", lambda *args: None)
    response = app.predict(app.PredictionRequest(platform=platform, **payload))
    assert response["platform"] == platform
    assert response["is_fake"] in {0, 1}
    assert 0.0 <= response["probability"] <= 1.0


def test_instagram_sample_schema_is_processed(monkeypatch):
    app = load_prediction_app(monkeypatch)
    monkeypatch.setattr(app, "persist", lambda *args: None)
    response = asyncio.run(app.predict_bulk(upload("instagram.csv", (ROOT / "sample_bulk_test.csv").read_text(encoding="utf-8")), "instagram"))
    assert response["total_profiles"] == 10
    assert response["error_count"] == 0
    assert response["results"][0]["username"] == "real_user_alice"


def test_twitter_snake_case_schema_is_processed(monkeypatch):
    app = load_prediction_app(monkeypatch)
    monkeypatch.setattr(app, "persist", lambda *args: None)
    response = asyncio.run(app.predict_bulk(upload("twitter.csv", "username,retweet_count,mention_count,follower_count_twitter,verified\nuser_x,8,1,3000,1\n"), "twitter"))
    assert response["total_profiles"] == 1
    assert response["error_count"] == 0
    assert response["results"][0]["username"] == "user_x"


def test_twitter_sample_bulk_file_is_processed(monkeypatch):
    app = load_prediction_app(monkeypatch)
    monkeypatch.setattr(app, "persist", lambda *args: None)
    response = asyncio.run(app.predict_bulk(upload("twitter_sample.csv", (ROOT / "sample_twitter_bulk.csv").read_text(encoding="utf-8")), "twitter"))
    assert response["total_profiles"] == 10
    assert response["error_count"] == 0
    assert response["results"][0]["username"] == "techwriter_mike"


@pytest.mark.parametrize("content,detail", [("", "header row"), ("username\nuser\n", "supported instagram")])
def test_invalid_bulk_csv_is_rejected(monkeypatch, content, detail):
    app = load_prediction_app(monkeypatch)
    with pytest.raises(HTTPException) as error:
        asyncio.run(app.predict_bulk(upload("invalid.csv", content), "instagram"))
    assert error.value.status_code == 400
    assert detail in error.value.detail
