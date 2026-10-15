"""Prediction service for FakeGuard AI.

This service owns ML inference only. Completed predictions are persisted through
the History Service HTTP API so prediction replicas remain stateless.
"""
import csv
import io
import json
import os
import pickle
import time
from typing import Literal, Optional

import httpx
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI(title="FakeGuard Prediction Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MODEL_DIR = os.getenv("MODEL_DIR", "/app/models")
HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://history-service:8001").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("HISTORY_REQUEST_TIMEOUT_SECONDS", "5"))

with open(os.path.join(MODEL_DIR, "insta_model.pkl"), "rb") as model_file:
    insta_model = pickle.load(model_file)
with open(os.path.join(MODEL_DIR, "insta_scaler.pkl"), "rb") as scaler_file:
    insta_scaler = pickle.load(scaler_file)
with open(os.path.join(MODEL_DIR, "insta_metadata.json"), encoding="utf-8") as metadata_file:
    insta_metadata = json.load(metadata_file)
with open(os.path.join(MODEL_DIR, "twitter_model.pkl"), "rb") as model_file:
    twitter_model = pickle.load(model_file)
with open(os.path.join(MODEL_DIR, "twitter_scaler.pkl"), "rb") as scaler_file:
    twitter_scaler = pickle.load(scaler_file)
with open(os.path.join(MODEL_DIR, "twitter_metadata.json"), encoding="utf-8") as metadata_file:
    twitter_metadata = json.load(metadata_file)


def validate_model_artifact(model, metadata, expected_features, platform):
    """Fail fast when a serialized model and its documented input schema differ."""
    metadata_features = metadata.get("feature_columns")
    if metadata_features != expected_features:
        raise RuntimeError(f"{platform} metadata feature schema does not match the service schema")
    model_features = getattr(model, "n_features_in_", len(expected_features))
    if model_features != len(expected_features):
        raise RuntimeError(f"{platform} model expects {model_features} features, not {len(expected_features)}")


validate_model_artifact(insta_model, insta_metadata, ["profile pic", "nums/length username", "fullname words", "nums/length fullname", "name==username", "description length", "external URL", "private", "#posts", "#followers", "#follows"], "instagram")
validate_model_artifact(twitter_model, twitter_metadata, ["Retweet Count", "Mention Count", "Follower Count", "Verified"], "twitter")

metrics = {"predictions_total": 0, "predictions_fake": 0, "predictions_real": 0, "predictions_instagram": 0, "predictions_twitter": 0, "requests_total": 0, "errors_total": 0, "bulk_uploads_total": 0, "request_duration_seconds_sum": 0.0, "request_duration_seconds_count": 0}


class PredictionRequest(BaseModel):
    platform: Literal["instagram", "twitter"]
    username: Optional[str] = ""
    profile_pic: Optional[int] = 1
    nums_length_username: Optional[float] = 0.0
    fullname_words: Optional[int] = 2
    nums_length_fullname: Optional[float] = 0.0
    name_eq_username: Optional[int] = 0
    description_length: Optional[int] = 50
    external_url: Optional[int] = 0
    private: Optional[int] = 0
    posts_count: Optional[int] = 100
    followers_count: Optional[float] = 500
    following_count: Optional[float] = 300
    retweet_count: Optional[int] = 30
    mention_count: Optional[int] = 2
    follower_count_twitter: Optional[int] = 3000
    verified: Optional[int] = 0


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    started = time.time()
    metrics["requests_total"] += 1
    try:
        return await call_next(request)
    except Exception:
        metrics["errors_total"] += 1
        raise
    finally:
        metrics["request_duration_seconds_sum"] += time.time() - started
        metrics["request_duration_seconds_count"] += 1


def risk_level(probability: float) -> str:
    if probability >= 0.85:
        return "critical"
    if probability >= 0.65:
        return "high"
    if probability >= 0.45:
        return "medium"
    return "low"


def explanation(profile: PredictionRequest, prediction: int) -> list[str]:
    values: list[str] = []
    if prediction == 1 and profile.platform == "instagram":
        if profile.profile_pic == 0: values.append("No profile picture — common in fake accounts")
        if profile.nums_length_username > 0.3: values.append("High proportion of numbers in username — bot-like pattern")
        if profile.fullname_words == 0: values.append("No fullname set — suspicious indicator")
        if profile.description_length == 0: values.append("Empty bio/description — typical of fake profiles")
        if profile.posts_count < 5: values.append("Very few posts — low activity")
    elif prediction == 1:
        if profile.retweet_count > 60: values.append("Very high retweet count — possible bot amplification")
        if profile.mention_count > 4: values.append("High mention count — possible spam behavior")
        if profile.follower_count_twitter < 100: values.append("Very low follower count")
        if profile.verified == 0: values.append("Not a verified account")
    elif profile.platform == "instagram":
        if profile.profile_pic == 1: values.append("Has a profile picture")
        if profile.description_length > 20: values.append("Detailed bio/description present")
        if profile.posts_count > 50: values.append("Active posting history")
    else:
        if profile.verified == 1: values.append("Verified account")
        if profile.follower_count_twitter > 1000: values.append("Strong follower base")
    return (values or (["Multiple behavioral signals indicate suspicious patterns"] if prediction else ["Profile shows characteristics of a genuine account"]))[:6]


def classify(profile: PredictionRequest) -> dict:
    if profile.platform == "instagram":
        model, metadata = insta_model, insta_metadata
        values = [profile.profile_pic, profile.nums_length_username, profile.fullname_words, profile.nums_length_fullname, profile.name_eq_username, profile.description_length, profile.external_url, profile.private, profile.posts_count, profile.followers_count, profile.following_count]
        metrics["predictions_instagram"] += 1
    else:
        model, metadata = twitter_model, twitter_metadata
        values = [profile.retweet_count, profile.mention_count, profile.follower_count_twitter, profile.verified]
        metrics["predictions_twitter"] += 1
    features = pd.DataFrame([values], columns=metadata["feature_columns"])
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    level = risk_level(probability)
    metrics["predictions_total"] += 1
    metrics["predictions_fake" if prediction else "predictions_real"] += 1
    return {"platform": profile.platform, "is_fake": prediction, "probability": round(probability, 4), "label": "Fake Profile" if prediction else "Real Profile", "risk_level": level, "feature_importance": metadata.get("feature_importance", {}), "explanation": explanation(profile, prediction)}


def persist(profile: PredictionRequest, result: dict, source: str) -> None:
    if profile.platform == "instagram":
        followers, following, posts = profile.followers_count, profile.following_count, profile.posts_count
        ratio, bio = followers / max(following, 1), profile.description_length
    else:
        followers, following, posts, ratio, bio = profile.follower_count_twitter, 0, 0, 0, 0
    record = {"platform": profile.platform, "username": profile.username or "", "followers_count": followers, "following_count": following, "follower_ratio": round(ratio, 4), "posts_or_tweets": posts, "bio_length": bio, "engagement_rate": 0, "prediction": result["is_fake"], "probability": result["probability"], "risk_level": result["risk_level"], "source": source}
    try:
        response = httpx.post(f"{HISTORY_SERVICE_URL}/records", json=record, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="History service is unavailable; prediction was not persisted") from exc


@app.get("/")
def health():
    return {"status": "ok", "service": "prediction", "models": [insta_metadata["best_model"], twitter_metadata["best_model"]]}


@app.post("/predict")
def predict(profile: PredictionRequest):
    result = classify(profile)
    persist(profile, result, "manual")
    return result


@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...), platform: Literal["instagram", "twitter"] = "instagram"):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    metrics["bulk_uploads_total"] += 1
    results = []
    for index, row in enumerate(csv.DictReader(io.StringIO((await file.read()).decode("utf-8")))):
        try:
            profile = PredictionRequest(platform=platform, username=row.get("username", f"user_{index}"), profile_pic=int(float(row.get("profile pic", 1))), nums_length_username=float(row.get("nums/length username", 0)), fullname_words=int(float(row.get("fullname words", 2))), nums_length_fullname=float(row.get("nums/length fullname", 0)), name_eq_username=int(float(row.get("name==username", 0)),), description_length=int(float(row.get("description length", 50))), external_url=int(float(row.get("external URL", 0))), private=int(float(row.get("private", 0))), posts_count=int(float(row.get("#posts", 100))), followers_count=float(row.get("#followers", 500)), following_count=float(row.get("#follows", 300)), retweet_count=int(float(row.get("Retweet Count", 30))), mention_count=int(float(row.get("Mention Count", 2))), follower_count_twitter=int(float(row.get("Follower Count", 3000))), verified=int(float(row.get("Verified", 0))))
            result = classify(profile)
            persist(profile, result, "bulk")
            results.append({"username": profile.username, "is_fake": result["is_fake"], "probability": result["probability"], "label": "Fake" if result["is_fake"] else "Real", "risk_level": result["risk_level"]})
        except Exception as exc:
            results.append({"username": row.get("username", f"user_{index}"), "error": str(exc)})
    return {"platform": platform, "total_profiles": len(results), "fake_count": sum(item.get("is_fake") == 1 for item in results), "real_count": sum(item.get("is_fake") == 0 for item in results), "error_count": sum("error" in item for item in results), "results": results}


@app.get("/model-info")
def model_info(platform: Optional[Literal["instagram", "twitter"]] = None):
    metadata = {"instagram": insta_metadata, "twitter": twitter_metadata}
    models = {"instagram": insta_model, "twitter": twitter_model}
    return {key: {"model_name": value.get("best_model", "Unknown"), "model_class": type(models[key]).__name__, "dataset_source": "existing trained dataset", "feature_columns": value.get("feature_columns", []), "feature_names": value.get("feature_names_display", []), "feature_importance": value.get("feature_importance", {}), "training_results": value.get("results", {}), "cross_validation_results": value.get("cross_validation_results", {}), "majority_baseline": value.get("majority_baseline", {}), "evaluation": value.get("evaluation", {}), "quality": value.get("quality", {"status": "unknown"}), "training_samples": value.get("training_samples", 0), "test_samples": value.get("test_samples", 0), "total_samples": value.get("total_samples", 0)} for key, value in metadata.items() if platform is None or key == platform}


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    lines = [f"{key} {value:.4f}" if isinstance(value, float) else f"{key} {value}" for key, value in metrics.items()]
    return "\n".join(lines) + "\n"
