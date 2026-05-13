"""
FastAPI Backend for Platform-Aware Fake Profile Detection System.
Uses REAL datasets from instagram1/2 and twitter1 directories.
Supports separate models for Instagram and Twitter.
Provides prediction, bulk upload, history, dashboard, and Prometheus metrics.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import pickle
import numpy as np
import json
import os
import io
import csv
import sqlite3
import time
from datetime import datetime
from contextlib import contextmanager

# ===================== APP SETUP =====================

app = FastAPI(
    title="Platform-Aware Fake Profile Detector API",
    description="ML-powered API for detecting fake social media profiles on Instagram & Twitter",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== PROMETHEUS METRICS =====================

metrics = {
    "predictions_total": 0,
    "predictions_fake": 0,
    "predictions_real": 0,
    "predictions_instagram": 0,
    "predictions_twitter": 0,
    "requests_total": 0,
    "errors_total": 0,
    "bulk_uploads_total": 0,
    "request_duration_seconds_sum": 0.0,
    "request_duration_seconds_count": 0,
}


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Middleware to track request metrics for Prometheus."""
    start_time = time.time()
    metrics["requests_total"] += 1
    try:
        response = await call_next(request)
        return response
    except Exception:
        metrics["errors_total"] += 1
        raise
    finally:
        duration = time.time() - start_time
        metrics["request_duration_seconds_sum"] += duration
        metrics["request_duration_seconds_count"] += 1


# ===================== LOAD MODELS =====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')
DB_PATH = os.path.join(BASE_DIR, 'predictions.db')

# Load Instagram model (trained on instagram1 + instagram2 datasets)
insta_model = pickle.load(open(os.path.join(MODEL_DIR, 'insta_model.pkl'), 'rb'))
insta_scaler = pickle.load(open(os.path.join(MODEL_DIR, 'insta_scaler.pkl'), 'rb'))
with open(os.path.join(MODEL_DIR, 'insta_metadata.json'), 'r') as f:
    insta_metadata = json.load(f)

# Load Twitter model (trained on twitter1 dataset)
twitter_model = pickle.load(open(os.path.join(MODEL_DIR, 'twitter_model.pkl'), 'rb'))
twitter_scaler = pickle.load(open(os.path.join(MODEL_DIR, 'twitter_scaler.pkl'), 'rb'))
with open(os.path.join(MODEL_DIR, 'twitter_metadata.json'), 'r') as f:
    twitter_metadata = json.load(f)

print(f"✅ Instagram model loaded: {insta_metadata['best_model']}")
print(f"✅ Twitter model loaded:   {twitter_metadata['best_model']}")

# ===================== DATABASE =====================

def init_db():
    """Initialize SQLite database for storing prediction history."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                platform TEXT NOT NULL,
                username TEXT DEFAULT '',
                followers_count REAL,
                following_count REAL,
                follower_ratio REAL,
                posts_or_tweets REAL,
                bio_length REAL,
                engagement_rate REAL,
                prediction INTEGER,
                probability REAL,
                risk_level TEXT,
                source TEXT DEFAULT 'manual'
            )
        ''')
        conn.commit()

init_db()


@contextmanager
def get_db():
    """Database connection context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ===================== SCHEMAS =====================
# Matching REAL dataset columns:
# Instagram: profile pic, nums/length username, fullname words, nums/length fullname,
#            name==username, description length, external URL, private, #posts, #followers, #follows
# Twitter:   Retweet Count, Mention Count, Follower Count, Verified

class PredictionRequest(BaseModel):
    """Unified prediction request that accepts either platform."""
    platform: Literal['instagram', 'twitter']
    username: Optional[str] = ""

    # ---- Instagram fields (from instagram1/instagram2 datasets) ----
    profile_pic: Optional[int] = 1               # 'profile pic': 0 or 1
    nums_length_username: Optional[float] = 0.0   # 'nums/length username': ratio
    fullname_words: Optional[int] = 2             # 'fullname words': count
    nums_length_fullname: Optional[float] = 0.0   # 'nums/length fullname': ratio
    name_eq_username: Optional[int] = 0           # 'name==username': 0 or 1
    description_length: Optional[int] = 50        # 'description length': chars
    external_url: Optional[int] = 0               # 'external URL': 0 or 1
    private: Optional[int] = 0                    # 'private': 0 or 1
    posts_count: Optional[int] = 100              # '#posts'
    followers_count: Optional[float] = 500        # '#followers'
    following_count: Optional[float] = 300        # '#follows'

    # ---- Twitter fields (from twitter1 dataset) ----
    retweet_count: Optional[int] = 30             # 'Retweet Count'
    mention_count: Optional[int] = 2              # 'Mention Count'
    follower_count_twitter: Optional[int] = 3000  # 'Follower Count'
    verified: Optional[int] = 0                   # 'Verified': 0 or 1


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    platform: str
    is_fake: int
    probability: float
    label: str
    risk_level: str
    feature_importance: dict
    explanation: List[str]

# ===================== HELPER FUNCTIONS =====================

def prepare_instagram_features(profile: PredictionRequest) -> np.ndarray:
    """Convert Instagram profile input to feature array.
    
    Features match training order from instagram1/instagram2 datasets:
    profile pic, nums/length username, fullname words, nums/length fullname,
    name==username, description length, external URL, private, #posts, #followers, #follows
    """
    features = [
        profile.profile_pic,
        profile.nums_length_username,
        profile.fullname_words,
        profile.nums_length_fullname,
        profile.name_eq_username,
        profile.description_length,
        profile.external_url,
        profile.private,
        profile.posts_count,
        profile.followers_count,
        profile.following_count,
    ]
    return np.array([features])


def prepare_twitter_features(profile: PredictionRequest) -> np.ndarray:
    """Convert Twitter profile input to feature array.
    
    Features match training order from twitter1 dataset:
    Retweet Count, Mention Count, Follower Count, Verified
    """
    features = [
        profile.retweet_count,
        profile.mention_count,
        profile.follower_count_twitter,
        profile.verified,
    ]
    return np.array([features])


def get_risk_level(probability: float) -> str:
    """Determine risk level based on fake probability."""
    if probability >= 0.85:
        return "critical"
    elif probability >= 0.65:
        return "high"
    elif probability >= 0.45:
        return "medium"
    else:
        return "low"


def generate_explanation(profile: PredictionRequest, prediction: int, platform: str) -> List[str]:
    """Generate human-readable explanation for the prediction (Explainable AI)."""
    explanations = []

    if prediction == 1:  # Fake
        if platform == 'instagram':
            if profile.profile_pic == 0:
                explanations.append("🚫 No profile picture — common in fake accounts")
            if profile.nums_length_username > 0.3:
                explanations.append("🔢 High proportion of numbers in username — bot-like pattern")
            if profile.fullname_words == 0:
                explanations.append("📝 No fullname set — suspicious indicator")
            if profile.description_length == 0:
                explanations.append("📝 Empty bio/description — typical of fake profiles")
            if profile.posts_count < 5:
                explanations.append("📸 Very few posts — low activity")
            if profile.followers_count < 10 and profile.following_count > 100:
                explanations.append("⚠️ Following many but very few followers")
            if profile.name_eq_username == 1 and profile.nums_length_username > 0.2:
                explanations.append("🤖 Username matches name with numbers — auto-generated")
        elif platform == 'twitter':
            if profile.retweet_count > 60:
                explanations.append("🔄 Very high retweet count — possible bot amplification")
            if profile.mention_count > 4:
                explanations.append("💬 High mention count — possible spam behavior")
            if profile.follower_count_twitter < 100:
                explanations.append("👤 Very low follower count")
            if profile.verified == 0:
                explanations.append("❌ Not a verified account")

        if not explanations:
            explanations.append("🔍 Multiple behavioral signals indicate suspicious patterns")
    else:  # Real
        if platform == 'instagram':
            if profile.profile_pic == 1:
                explanations.append("✅ Has a profile picture")
            if profile.description_length > 20:
                explanations.append("📝 Detailed bio/description present")
            if profile.posts_count > 50:
                explanations.append("📸 Active posting history")
            if profile.followers_count > 100:
                explanations.append("📊 Healthy follower count")
        elif platform == 'twitter':
            if profile.verified == 1:
                explanations.append("✔️ Verified account")
            if profile.follower_count_twitter > 1000:
                explanations.append("📊 Strong follower base")
            if profile.mention_count < 3:
                explanations.append("💬 Normal mention activity")

        if not explanations:
            explanations.append("✅ Profile shows characteristics of a genuine account")

    return explanations[:6]


def save_prediction(profile: PredictionRequest, prediction: int, probability: float,
                    risk_level: str, source: str = "manual"):
    """Save prediction to SQLite database."""
    if profile.platform == 'instagram':
        ratio = profile.followers_count / max(profile.following_count, 1)
        posts = profile.posts_count
    else:
        ratio = 0
        posts = 0

    with get_db() as conn:
        conn.execute('''
            INSERT INTO predictions (
                timestamp, platform, username, followers_count, following_count,
                follower_ratio, posts_or_tweets, bio_length,
                engagement_rate, prediction, probability, risk_level, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            profile.platform, profile.username or '',
            profile.followers_count if profile.platform == 'instagram' else profile.follower_count_twitter,
            profile.following_count if profile.platform == 'instagram' else 0,
            round(ratio, 4), posts or 0,
            profile.description_length if profile.platform == 'instagram' else 0,
            0, prediction, probability, risk_level, source
        ))
        conn.commit()


# ===================== ROUTES =====================

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Platform-Aware Fake Profile Detector API",
        "version": "2.0.0",
        "platforms": ["instagram", "twitter"],
        "models": {
            "instagram": insta_metadata['best_model'],
            "twitter": twitter_metadata['best_model']
        },
        "datasets_used": {
            "instagram": "instagram1/ (5001 profiles) + instagram2/ (train+test)",
            "twitter": "twitter1/bot_detection_data.csv (50000 tweets)"
        },
        "endpoints": ["/predict", "/predict/bulk", "/history", "/dashboard", "/model-info", "/metrics"]
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(profile: PredictionRequest):
    """Predict if a social media profile is fake or real.
    
    Automatically selects the correct model based on the platform field.
    Instagram model trained on: profile pic, username pattern, fullname, bio, posts, followers, following
    Twitter model trained on: retweet count, mention count, follower count, verified status
    """
    try:
        if profile.platform == 'instagram':
            features = prepare_instagram_features(profile)
            model = insta_model
            metadata = insta_metadata
            metrics["predictions_instagram"] += 1
        elif profile.platform == 'twitter':
            features = prepare_twitter_features(profile)
            model = twitter_model
            metadata = twitter_metadata
            metrics["predictions_twitter"] += 1
        else:
            raise HTTPException(status_code=400, detail="Platform must be 'instagram' or 'twitter'")

        # Run prediction
        prediction = int(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
        probability = float(probabilities[1])

        risk_level = get_risk_level(probability)
        explanation = generate_explanation(profile, prediction, profile.platform)

        # Update metrics
        metrics["predictions_total"] += 1
        if prediction == 1:
            metrics["predictions_fake"] += 1
        else:
            metrics["predictions_real"] += 1

        # Save to database
        save_prediction(profile, prediction, probability, risk_level)

        return PredictionResponse(
            platform=profile.platform,
            is_fake=prediction,
            probability=round(probability, 4),
            label="Fake Profile" if prediction == 1 else "Real Profile",
            risk_level=risk_level,
            feature_importance=metadata.get('feature_importance', {}),
            explanation=explanation
        )

    except Exception as e:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...), platform: str = "instagram"):
    """Bulk predict from CSV upload for a specific platform."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    if platform not in ('instagram', 'twitter'):
        raise HTTPException(status_code=400, detail="Platform must be 'instagram' or 'twitter'")

    contents = await file.read()
    reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))
    metrics["bulk_uploads_total"] += 1

    results = []
    for i, row in enumerate(reader):
        try:
            profile = PredictionRequest(
                platform=platform,
                username=row.get('username', f'user_{i}'),
                # Instagram fields
                profile_pic=int(float(row.get('profile pic', 1))),
                nums_length_username=float(row.get('nums/length username', 0)),
                fullname_words=int(float(row.get('fullname words', 2))),
                nums_length_fullname=float(row.get('nums/length fullname', 0)),
                name_eq_username=int(float(row.get('name==username', 0))),
                description_length=int(float(row.get('description length', 50))),
                external_url=int(float(row.get('external URL', 0))),
                private=int(float(row.get('private', 0))),
                posts_count=int(float(row.get('#posts', 100))),
                followers_count=float(row.get('#followers', 500)),
                following_count=float(row.get('#follows', 300)),
                # Twitter fields
                retweet_count=int(float(row.get('Retweet Count', 30))),
                mention_count=int(float(row.get('Mention Count', 2))),
                follower_count_twitter=int(float(row.get('Follower Count', 3000))),
                verified=int(float(row.get('Verified', 0))),
            )

            if platform == 'instagram':
                features = prepare_instagram_features(profile)
                model = insta_model
            else:
                features = prepare_twitter_features(profile)
                model = twitter_model

            prediction = int(model.predict(features)[0])
            probabilities = model.predict_proba(features)[0]
            probability = float(probabilities[1])
            risk_level = get_risk_level(probability)

            save_prediction(profile, prediction, probability, risk_level, source="bulk")

            results.append({
                "username": profile.username,
                "is_fake": prediction,
                "probability": round(probability, 4),
                "label": "Fake" if prediction == 1 else "Real",
                "risk_level": risk_level
            })
        except Exception as e:
            results.append({
                "username": row.get('username', f'user_{i}'),
                "error": str(e)
            })

    total = len(results)
    fake_count = sum(1 for r in results if r.get('is_fake') == 1)
    real_count = sum(1 for r in results if r.get('is_fake') == 0)
    error_count = sum(1 for r in results if 'error' in r)

    return {
        "platform": platform,
        "total_profiles": total,
        "fake_count": fake_count,
        "real_count": real_count,
        "error_count": error_count,
        "results": results
    }


@app.get("/history")
def get_history(limit: int = 50, offset: int = 0, platform: str = None):
    """Get prediction history, optionally filtered by platform."""
    with get_db() as conn:
        if platform:
            rows = conn.execute(
                'SELECT * FROM predictions WHERE platform = ? ORDER BY id DESC LIMIT ? OFFSET ?',
                (platform, limit, offset)
            ).fetchall()
            total = conn.execute(
                'SELECT COUNT(*) FROM predictions WHERE platform = ?', (platform,)
            ).fetchone()[0]
        else:
            rows = conn.execute(
                'SELECT * FROM predictions ORDER BY id DESC LIMIT ? OFFSET ?',
                (limit, offset)
            ).fetchall()
            total = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "platform_filter": platform,
        "predictions": [dict(row) for row in rows]
    }


@app.get("/dashboard")
def get_dashboard():
    """Get analytics dashboard data with platform breakdown."""
    with get_db() as conn:
        total = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]

        if total == 0:
            return {
                "total_scans": 0, "fake_count": 0, "real_count": 0,
                "fake_percentage": 0, "avg_probability": 0,
                "platform_breakdown": {"instagram": {"total": 0, "fake": 0, "real": 0},
                                       "twitter": {"total": 0, "fake": 0, "real": 0}},
                "risk_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "recent_predictions": [], "daily_stats": []
            }

        fake_count = conn.execute(
            'SELECT COUNT(*) FROM predictions WHERE prediction = 1'
        ).fetchone()[0]
        real_count = total - fake_count

        avg_prob = conn.execute(
            'SELECT AVG(probability) FROM predictions'
        ).fetchone()[0] or 0

        # Platform breakdown
        platform_breakdown = {}
        for plat in ['instagram', 'twitter']:
            p_total = conn.execute(
                'SELECT COUNT(*) FROM predictions WHERE platform = ?', (plat,)
            ).fetchone()[0]
            p_fake = conn.execute(
                'SELECT COUNT(*) FROM predictions WHERE platform = ? AND prediction = 1', (plat,)
            ).fetchone()[0]
            platform_breakdown[plat] = {
                "total": p_total, "fake": p_fake, "real": p_total - p_fake
            }

        # Risk distribution
        risk_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        rows = conn.execute('SELECT risk_level FROM predictions WHERE prediction = 1').fetchall()
        for row in rows:
            level = row['risk_level']
            if level in risk_dist:
                risk_dist[level] += 1

        # Recent predictions
        recent = conn.execute(
            'SELECT * FROM predictions ORDER BY id DESC LIMIT 10'
        ).fetchall()

        # Daily stats
        daily = conn.execute('''
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as total,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fake,
                SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as real_count
            FROM predictions
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 7
        ''').fetchall()

    return {
        "total_scans": total,
        "fake_count": fake_count,
        "real_count": real_count,
        "fake_percentage": round(fake_count / total * 100, 1) if total else 0,
        "avg_probability": round(avg_prob, 4),
        "platform_breakdown": platform_breakdown,
        "risk_distribution": risk_dist,
        "recent_predictions": [dict(r) for r in recent],
        "daily_stats": [dict(d) for d in daily]
    }


@app.get("/model-info")
def get_model_info(platform: str = None):
    """Get model information for one or both platforms."""
    info = {}

    if platform is None or platform == 'instagram':
        info['instagram'] = {
            "model_name": insta_metadata.get('best_model', 'Unknown'),
            "dataset_source": "instagram1/Instagram_fake_profile_dataset.csv + instagram2/train.csv + instagram2/test.csv",
            "feature_columns": insta_metadata.get('feature_columns', []),
            "feature_names": insta_metadata.get('feature_names_display', []),
            "feature_importance": insta_metadata.get('feature_importance', {}),
            "training_results": insta_metadata.get('results', {}),
            "training_samples": insta_metadata.get('training_samples', 0),
            "test_samples": insta_metadata.get('test_samples', 0),
            "total_samples": insta_metadata.get('total_samples', 0),
        }

    if platform is None or platform == 'twitter':
        info['twitter'] = {
            "model_name": twitter_metadata.get('best_model', 'Unknown'),
            "dataset_source": "twitter1/bot_detection_data.csv (50K tweets, bot detection)",
            "feature_columns": twitter_metadata.get('feature_columns', []),
            "feature_names": twitter_metadata.get('feature_names_display', []),
            "feature_importance": twitter_metadata.get('feature_importance', {}),
            "training_results": twitter_metadata.get('results', {}),
            "training_samples": twitter_metadata.get('training_samples', 0),
            "test_samples": twitter_metadata.get('test_samples', 0),
            "total_samples": twitter_metadata.get('total_samples', 0),
        }

    return info


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    """Expose metrics in Prometheus text format for scraping."""
    lines = []
    lines.append("# HELP predictions_total Total number of predictions made")
    lines.append("# TYPE predictions_total counter")
    lines.append(f'predictions_total {metrics["predictions_total"]}')
    
    lines.append("# HELP predictions_fake Total fake predictions")
    lines.append("# TYPE predictions_fake counter")
    lines.append(f'predictions_fake {metrics["predictions_fake"]}')
    
    lines.append("# HELP predictions_real Total real predictions")
    lines.append("# TYPE predictions_real counter")
    lines.append(f'predictions_real {metrics["predictions_real"]}')
    
    lines.append("# HELP predictions_instagram Instagram predictions")
    lines.append("# TYPE predictions_instagram counter")
    lines.append(f'predictions_instagram {metrics["predictions_instagram"]}')
    
    lines.append("# HELP predictions_twitter Twitter predictions")
    lines.append("# TYPE predictions_twitter counter")
    lines.append(f'predictions_twitter {metrics["predictions_twitter"]}')
    
    lines.append("# HELP requests_total Total HTTP requests")
    lines.append("# TYPE requests_total counter")
    lines.append(f'requests_total {metrics["requests_total"]}')
    
    lines.append("# HELP errors_total Total errors")
    lines.append("# TYPE errors_total counter")
    lines.append(f'errors_total {metrics["errors_total"]}')
    
    lines.append("# HELP bulk_uploads_total Total bulk uploads")
    lines.append("# TYPE bulk_uploads_total counter")
    lines.append(f'bulk_uploads_total {metrics["bulk_uploads_total"]}')
    
    lines.append("# HELP request_duration_seconds Total request duration")
    lines.append("# TYPE request_duration_seconds summary")
    lines.append(f'request_duration_seconds_sum {metrics["request_duration_seconds_sum"]:.4f}')
    lines.append(f'request_duration_seconds_count {metrics["request_duration_seconds_count"]}')
    
    return "\n".join(lines) + "\n"


@app.delete("/history/clear")
def clear_history():
    """Clear all prediction history."""
    with get_db() as conn:
        conn.execute('DELETE FROM predictions')
        conn.commit()
    return {"message": "History cleared"}
