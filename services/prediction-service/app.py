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

BULK_COLUMN_ALIASES = {
    "instagram": {
        "profile_pic": ("profile pic", "profile_pic", "has_profile_pic"),
        "nums_length_username": ("nums/length username", "nums_length_username"),
        "fullname_words": ("fullname words", "fullname_words"),
        "nums_length_fullname": ("nums/length fullname", "nums_length_fullname"),
        "name_eq_username": ("name==username", "name_eq_username"),
        "description_length": ("description length", "description_length", "bio_length"),
        "external_url": ("external URL", "external_url", "has_url_in_bio"),
        "private": ("private", "is_private"),
        "posts_count": ("#posts", "posts_count"),
        "followers_count": ("#followers", "followers_count", "follower_count"),
        "following_count": ("#follows", "following_count"),
    },
    "twitter": {
        "retweet_count": ("Retweet Count", "retweet_count", "avg_retweets"),
        "mention_count": ("Mention Count", "mention_count"),
        "follower_count_twitter": ("Follower Count", "follower_count_twitter", "followers_count"),
        "verified": ("Verified", "verified", "is_verified"),
    },
}


class PredictionRequest(BaseModel):
    platform: Literal["instagram", "twitter"]
    username: Optional[str] = ""
    profile_pic: Optional[int] = None
    has_profile_pic: Optional[int] = None
    nums_length_username: Optional[float] = 0.0
    fullname_words: Optional[int] = 2
    nums_length_fullname: Optional[float] = 0.0
    name_eq_username: Optional[int] = 0
    description_length: Optional[int] = None
    bio_length: Optional[int] = None
    external_url: Optional[int] = None
    has_url_in_bio: Optional[int] = None
    private: Optional[int] = None
    is_private: Optional[int] = None
    posts_count: Optional[int] = 100
    followers_count: Optional[float] = None
    following_count: Optional[float] = 300
    retweet_count: Optional[int] = None
    avg_retweets: Optional[int] = None
    mention_count: Optional[int] = 2
    follower_count_twitter: Optional[int] = None
    follower_count: Optional[int] = None
    verified: Optional[int] = None
    is_verified: Optional[int] = None


def resolve_features(profile: PredictionRequest):
    """Normalize input fields across model parameter names and UI/bulk aliases."""
    if profile.platform == "instagram":
        p_pic = profile.profile_pic if profile.profile_pic is not None else (profile.has_profile_pic if profile.has_profile_pic is not None else 1)
        desc_len = profile.description_length if profile.description_length is not None else (profile.bio_length if profile.bio_length is not None else 50)
        ext_url = profile.external_url if profile.external_url is not None else (profile.has_url_in_bio if profile.has_url_in_bio is not None else 0)
        priv = profile.private if profile.private is not None else (profile.is_private if profile.is_private is not None else 0)
        followers = profile.followers_count if profile.followers_count is not None else 500.0
        following = profile.following_count if profile.following_count is not None else 300.0
        posts = profile.posts_count if profile.posts_count is not None else 100
        return {
            "profile_pic": int(p_pic),
            "nums_length_username": float(profile.nums_length_username or 0.0),
            "fullname_words": int(profile.fullname_words if profile.fullname_words is not None else 2),
            "nums_length_fullname": float(profile.nums_length_fullname or 0.0),
            "name_eq_username": int(profile.name_eq_username or 0),
            "description_length": int(desc_len),
            "external_url": int(ext_url),
            "private": int(priv),
            "posts_count": int(posts),
            "followers_count": float(followers),
            "following_count": float(following),
        }
    retweet = profile.retweet_count if profile.retweet_count is not None else (profile.avg_retweets if profile.avg_retweets is not None else 30)
    mention = profile.mention_count if profile.mention_count is not None else 2
    followers = profile.follower_count_twitter if profile.follower_count_twitter is not None else (profile.follower_count if profile.follower_count is not None else (int(profile.followers_count) if profile.followers_count is not None else 3000))
    ver = profile.verified if profile.verified is not None else (profile.is_verified if profile.is_verified is not None else 0)
    return {
        "retweet_count": int(retweet),
        "mention_count": int(mention),
        "follower_count_twitter": int(followers),
        "verified": int(ver),
    }


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
    f = resolve_features(profile)
    values: list[str] = []
    if prediction == 1 and profile.platform == "instagram":
        if f["profile_pic"] == 0: values.append("No profile picture — common in fake accounts")
        if f["nums_length_username"] > 0.3: values.append("High proportion of numbers in username — bot-like pattern")
        if f["fullname_words"] == 0: values.append("No fullname set — suspicious indicator")
        if f["description_length"] == 0: values.append("Empty bio/description — typical of fake profiles")
        if f["posts_count"] < 5: values.append("Very few posts — low activity")
    elif prediction == 1:
        if f["retweet_count"] > 60: values.append("Very high retweet count — possible bot amplification")
        if f["mention_count"] > 4: values.append("High mention count — possible spam behavior")
        if f["follower_count_twitter"] < 100: values.append("Very low follower count")
        if f["verified"] == 0: values.append("Not a verified account")
    elif profile.platform == "instagram":
        if f["profile_pic"] == 1: values.append("Has a profile picture")
        if f["description_length"] > 20: values.append("Detailed bio/description present")
        if f["posts_count"] > 50: values.append("Active posting history")
    else:
        if f["verified"] == 1: values.append("Verified account")
        if f["follower_count_twitter"] > 1000: values.append("Strong follower base")
    return (values or (["Multiple behavioral signals indicate suspicious patterns"] if prediction else ["Profile shows characteristics of a genuine account"]))[:6]


def record_prediction(platform: str, prediction: int) -> None:
    if platform == "instagram":
        metrics["predictions_instagram"] += 1
    else:
        metrics["predictions_twitter"] += 1
    metrics["predictions_total"] += 1
    if prediction == 1:
        metrics["predictions_fake"] += 1
    else:
        metrics["predictions_real"] += 1


def classify(profile: PredictionRequest) -> dict:
    f = resolve_features(profile)
    if profile.platform == "instagram":
        model, metadata = insta_model, insta_metadata
        values = [f["profile_pic"], f["nums_length_username"], f["fullname_words"], f["nums_length_fullname"], f["name_eq_username"], f["description_length"], f["external_url"], f["private"], f["posts_count"], f["followers_count"], f["following_count"]]
    else:
        model, metadata = twitter_model, twitter_metadata
        values = [f["retweet_count"], f["mention_count"], f["follower_count_twitter"], f["verified"]]
    features = pd.DataFrame([values], columns=metadata["feature_columns"])
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    level = risk_level(probability)
    return {"platform": profile.platform, "is_fake": prediction, "probability": round(probability, 4), "label": "Fake Profile" if prediction else "Real Profile", "risk_level": level, "feature_importance": metadata.get("feature_importance", {}), "explanation": explanation(profile, prediction)}


def persist(profile: PredictionRequest, result: dict, source: str) -> None:
    f = resolve_features(profile)
    if profile.platform == "instagram":
        followers, following, posts = f["followers_count"], f["following_count"], f["posts_count"]
        ratio, bio = followers / max(following, 1), f["description_length"]
    else:
        followers, following, posts, ratio, bio = f["follower_count_twitter"], 0, 0, 0, 0
    record = {"platform": profile.platform, "username": profile.username or "", "followers_count": followers, "following_count": following, "follower_ratio": round(ratio, 4), "posts_or_tweets": posts, "bio_length": bio, "engagement_rate": 0, "prediction": result["is_fake"], "probability": result["probability"], "risk_level": result["risk_level"], "source": source}
    try:
        response = httpx.post(f"{HISTORY_SERVICE_URL}/records", json=record, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="History service is unavailable; prediction was not persisted") from exc


def csv_key(column: str) -> str:
    return column.strip().lower()


def csv_value(row: dict, aliases: tuple[str, ...], default, converter):
    for alias in aliases:
        value = row.get(csv_key(alias))
        if value is not None and value.strip() != "":
            return converter(value)
    return default


def profile_from_csv_row(row: dict, platform: Literal["instagram", "twitter"], index: int) -> PredictionRequest:
    """Map documented model headers and the frontend sample headers to API fields."""
    try:
        username = csv_value(row, ("username", "user name"), f"user_{index}", str)
        aliases = BULK_COLUMN_ALIASES[platform]
        if platform == "instagram":
            return PredictionRequest(
                platform=platform, username=username,
                profile_pic=csv_value(row, aliases["profile_pic"], 1, lambda value: int(float(value))),
                nums_length_username=csv_value(row, aliases["nums_length_username"], 0.0, float),
                fullname_words=csv_value(row, aliases["fullname_words"], 2, lambda value: int(float(value))),
                nums_length_fullname=csv_value(row, aliases["nums_length_fullname"], 0.0, float),
                name_eq_username=csv_value(row, aliases["name_eq_username"], 0, lambda value: int(float(value))),
                description_length=csv_value(row, aliases["description_length"], 50, lambda value: int(float(value))),
                external_url=csv_value(row, aliases["external_url"], 0, lambda value: int(float(value))),
                private=csv_value(row, aliases["private"], 0, lambda value: int(float(value))),
                posts_count=csv_value(row, aliases["posts_count"], 100, lambda value: int(float(value))),
                followers_count=csv_value(row, aliases["followers_count"], 500.0, float),
                following_count=csv_value(row, aliases["following_count"], 300.0, float),
            )
        return PredictionRequest(
            platform=platform, username=username,
            retweet_count=csv_value(row, aliases["retweet_count"], 30, lambda value: int(float(value))),
            mention_count=csv_value(row, aliases["mention_count"], 2, lambda value: int(float(value))),
            follower_count_twitter=csv_value(row, aliases["follower_count_twitter"], 3000, lambda value: int(float(value))),
            verified=csv_value(row, aliases["verified"], 0, lambda value: int(float(value))),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric value in CSV row {index + 1}") from exc


@app.get("/")
def health():
    return {"status": "ok", "service": "prediction", "models": [insta_metadata["best_model"], twitter_metadata["best_model"]]}


@app.post("/predict")
def predict(profile: PredictionRequest):
    result = classify(profile)
    persist(profile, result, "manual")
    record_prediction(profile.platform, result["is_fake"])
    return result


@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...), platform: Literal["instagram", "twitter"] = "instagram"):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    try:
        content = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV must include a header row")
    fieldnames = {csv_key(name) for name in reader.fieldnames if name}
    supported_columns = {csv_key(alias) for aliases in BULK_COLUMN_ALIASES[platform].values() for alias in aliases}
    if not fieldnames.intersection(supported_columns):
        raise HTTPException(status_code=400, detail=f"CSV has no supported {platform} feature columns")
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="CSV contains no data rows")
    metrics["bulk_uploads_total"] += 1
    results = []
    for index, raw_row in enumerate(rows):
        row = {csv_key(key): value for key, value in raw_row.items() if key is not None}
        try:
            profile = profile_from_csv_row(row, platform, index)
            result = classify(profile)
            persist(profile, result, "bulk")
            record_prediction(profile.platform, result["is_fake"])
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
    lines = [
        "# HELP predictions_total Total number of predictions made",
        "# TYPE predictions_total counter",
        f"predictions_total {metrics['predictions_total']}",
        "# HELP predictions_fake Total fake predictions",
        "# TYPE predictions_fake counter",
        f"predictions_fake {metrics['predictions_fake']}",
        "# HELP predictions_real Total real predictions",
        "# TYPE predictions_real counter",
        f"predictions_real {metrics['predictions_real']}",
        "# HELP predictions_instagram Instagram predictions",
        "# TYPE predictions_instagram counter",
        f"predictions_instagram {metrics['predictions_instagram']}",
        "# HELP predictions_twitter Twitter predictions",
        "# TYPE predictions_twitter counter",
        f"predictions_twitter {metrics['predictions_twitter']}",
        "# HELP requests_total Total HTTP requests",
        "# TYPE requests_total counter",
        f"requests_total {metrics['requests_total']}",
        "# HELP errors_total Total HTTP errors",
        "# TYPE errors_total counter",
        f"errors_total {metrics['errors_total']}",
        "# HELP bulk_uploads_total Total bulk uploads",
        "# TYPE bulk_uploads_total counter",
        f"bulk_uploads_total {metrics['bulk_uploads_total']}",
        "# HELP request_duration_seconds Total request duration",
        "# TYPE request_duration_seconds summary",
        f"request_duration_seconds_sum {metrics['request_duration_seconds_sum']:.4f}",
        f"request_duration_seconds_count {metrics['request_duration_seconds_count']}",
    ]
    return "\n".join(lines) + "\n"
