"""
Basic tests for the FakeGuard API.
Run with: python -m pytest tests/ -v
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient


def get_client():
    """Create a test client for the FastAPI app."""
    from app import app
    return TestClient(app)


def test_health_check():
    """Test the root health check endpoint."""
    client = get_client()
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "2.0.0"
    assert "instagram" in data["platforms"]
    assert "twitter" in data["platforms"]


def test_predict_instagram_real():
    """Test prediction for a real Instagram profile."""
    client = get_client()
    payload = {
        "platform": "instagram",
        "username": "test_real_user",
        "followers_count": 4500,
        "following_count": 380,
        "posts_count": 340,
        "account_age_days": 1800,
        "bio_length": 90,
        "has_profile_pic": 1,
        "is_private": 0,
        "is_verified": 0,
        "has_url_in_bio": 1,
        "avg_likes": 180,
        "avg_comments": 12
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "instagram"
    assert "is_fake" in data
    assert "probability" in data
    assert "explanation" in data
    assert data["is_fake"] == 0  # Should be real


def test_predict_instagram_fake():
    """Test prediction for a fake Instagram profile."""
    client = get_client()
    payload = {
        "platform": "instagram",
        "username": "bot_account",
        "followers_count": 10,
        "following_count": 6000,
        "posts_count": 1,
        "account_age_days": 5,
        "bio_length": 0,
        "has_profile_pic": 0,
        "is_private": 0,
        "is_verified": 0,
        "has_url_in_bio": 1,
        "avg_likes": 0,
        "avg_comments": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_fake"] == 1  # Should be fake


def test_predict_twitter_real():
    """Test prediction for a real Twitter profile."""
    client = get_client()
    payload = {
        "platform": "twitter",
        "username": "real_tweeter",
        "followers_count": 3200,
        "following_count": 450,
        "tweets_count": 8500,
        "account_age_days": 2900,
        "bio_length": 110,
        "has_profile_pic": 1,
        "is_verified": 0,
        "has_url_in_bio": 1,
        "listed_count": 45,
        "avg_retweets": 8,
        "avg_favorites": 25,
        "reply_ratio": 0.25
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "twitter"
    assert data["is_fake"] == 0


def test_predict_twitter_fake():
    """Test prediction for a fake Twitter profile."""
    client = get_client()
    payload = {
        "platform": "twitter",
        "username": "spam_bot_x",
        "followers_count": 5,
        "following_count": 4800,
        "tweets_count": 2,
        "account_age_days": 3,
        "bio_length": 0,
        "has_profile_pic": 0,
        "is_verified": 0,
        "has_url_in_bio": 1,
        "listed_count": 0,
        "avg_retweets": 0,
        "avg_favorites": 0,
        "reply_ratio": 0.9
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_fake"] == 1


def test_model_info():
    """Test model info endpoint returns both platforms."""
    client = get_client()
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "instagram" in data
    assert "twitter" in data
    assert "model_name" in data["instagram"]
    assert "model_name" in data["twitter"]


def test_dashboard_empty():
    """Test dashboard returns valid structure."""
    client = get_client()
    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "platform_breakdown" in data


def test_history():
    """Test history endpoint."""
    client = get_client()
    response = client.get("/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "total" in data


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    client = get_client()
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "predictions_total" in response.text
    assert "requests_total" in response.text
    assert "predictions_instagram" in response.text
    assert "predictions_twitter" in response.text
