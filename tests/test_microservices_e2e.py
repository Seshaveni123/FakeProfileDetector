"""Run against a locally started Compose stack.

Set PREDICTION_SERVICE_URL=http://localhost:8000,
HISTORY_SERVICE_URL=http://localhost:8001, and
ANALYTICS_SERVICE_URL=http://localhost:8002 before invoking pytest.
"""
import os

import pytest
import requests

PREDICTION_URL = os.getenv("PREDICTION_SERVICE_URL")
HISTORY_URL = os.getenv("HISTORY_SERVICE_URL")
ANALYTICS_URL = os.getenv("ANALYTICS_SERVICE_URL")
pytestmark = pytest.mark.skipif(not all((PREDICTION_URL, HISTORY_URL, ANALYTICS_URL)), reason="set all three service URLs after starting Docker Compose")


def request(base_url, method, path, **kwargs):
    return requests.request(method, f"{base_url}{path}", timeout=15, **kwargs)


def test_health_and_prediction_persistence():
    assert request(PREDICTION_URL, "GET", "/").status_code == 200
    assert request(HISTORY_URL, "GET", "/").status_code == 200
    assert request(ANALYTICS_URL, "GET", "/").status_code == 200
    payload = {"platform": "instagram", "username": "microservice-test", "profile_pic": 1, "posts_count": 100, "followers_count": 500, "following_count": 100}
    prediction = request(PREDICTION_URL, "POST", "/predict", json=payload)
    assert prediction.status_code == 200
    assert {"is_fake", "probability", "risk_level", "explanation"} <= prediction.json().keys()
    twitter = request(PREDICTION_URL, "POST", "/predict", json={"platform": "twitter", "username": "microservice-twitter-test", "retweet_count": 8, "mention_count": 1, "follower_count_twitter": 3000, "verified": 1})
    assert twitter.status_code == 200


def test_history_and_clear():
    history = request(HISTORY_URL, "GET", "/history?limit=50")
    assert history.status_code == 200
    assert "predictions" in history.json()
    cleared = request(HISTORY_URL, "DELETE", "/history/clear")
    assert cleared.status_code == 200


def test_model_info_and_metrics():
    assert {"instagram", "twitter"} <= request(PREDICTION_URL, "GET", "/model-info").json().keys()
    assert request(PREDICTION_URL, "GET", "/metrics").status_code == 200
    assert request(ANALYTICS_URL, "GET", "/dashboard").status_code == 200
