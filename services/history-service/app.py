"""History service. Owns the shared PostgreSQL prediction history."""
import time
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Literal, Optional

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fakeguard:fakeguard@postgres:5432/fakeguard")
app = FastAPI(title="FakeGuard History Service", version="2.0.0")

metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "records_created_total": 0,
    "history_reads_total": 0,
    "request_duration_seconds_sum": 0.0,
    "request_duration_seconds_count": 0,
}


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    started = time.time()
    metrics["requests_total"] += 1
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            metrics["errors_total"] += 1
        return response
    except Exception:
        metrics["errors_total"] += 1
        raise
    finally:
        metrics["request_duration_seconds_sum"] += time.time() - started
        metrics["request_duration_seconds_count"] += 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    platform TEXT NOT NULL,
    username TEXT DEFAULT '',
    followers_count DOUBLE PRECISION,
    following_count DOUBLE PRECISION,
    follower_ratio DOUBLE PRECISION,
    posts_or_tweets DOUBLE PRECISION,
    bio_length DOUBLE PRECISION,
    engagement_rate DOUBLE PRECISION,
    prediction INTEGER,
    probability DOUBLE PRECISION,
    risk_level TEXT,
    source TEXT DEFAULT 'manual'
);
"""


class PredictionRecord(BaseModel):
    platform: Literal["instagram", "twitter"]
    username: str = ""
    followers_count: float = 0
    following_count: float = 0
    follower_ratio: float = 0
    posts_or_tweets: float = 0
    bio_length: float = 0
    engagement_rate: float = 0
    prediction: int
    probability: float
    risk_level: str
    source: str = "manual"


@contextmanager
def connection():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            yield conn
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="History database is unavailable") from exc



@app.on_event("startup")
def initialize_database():
    for attempt in range(10):
        try:
            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    # Prevent concurrent schema initialization.
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock(729104321)"
                    )
                    cursor.execute(SCHEMA)
                conn.commit()
            return
        except psycopg.OperationalError:
            if attempt == 9:
                raise
            time.sleep(3)



@app.get("/")
def health():
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    return {"status": "ok", "service": "history"}


@app.post("/records", status_code=201)
def create_record(record: PredictionRecord):
    statement = """INSERT INTO predictions (timestamp, platform, username, followers_count, following_count, follower_ratio, posts_or_tweets, bio_length, engagement_rate, prediction, probability, risk_level, source)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, timestamp"""
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement, (datetime.now(timezone.utc), record.platform, record.username, record.followers_count, record.following_count, record.follower_ratio, record.posts_or_tweets, record.bio_length, record.engagement_rate, record.prediction, record.probability, record.risk_level, record.source))
            record_id, timestamp = cursor.fetchone()
        conn.commit()
    metrics["records_created_total"] += 1
    return {"id": record_id, "timestamp": timestamp.isoformat()}


@app.get("/history")
def get_history(limit: int = 50, offset: int = 0, platform: Optional[Literal["instagram", "twitter"]] = None):
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    where, params = ("WHERE platform = %s", [platform]) if platform else ("", [])
    with connection() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute(f"SELECT COUNT(*) AS count FROM predictions {where}", params)
            total = cursor.fetchone()["count"]
            cursor.execute(f"SELECT * FROM predictions {where} ORDER BY id DESC LIMIT %s OFFSET %s", [*params, limit, offset])
            rows = cursor.fetchall()
    for row in rows:
        row["timestamp"] = row["timestamp"].isoformat()
    metrics["history_reads_total"] += 1
    return {"total": total, "limit": limit, "offset": offset, "platform_filter": platform, "predictions": rows}


@app.delete("/history/clear")
def clear_history():
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM predictions")
        conn.commit()
    return {"message": "History cleared"}


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    """Expose metrics in Prometheus text format."""
    lines = [
        "# HELP requests_total Total HTTP requests",
        "# TYPE requests_total counter",
        f"requests_total {metrics['requests_total']}",
        "# HELP errors_total Total HTTP errors",
        "# TYPE errors_total counter",
        f"errors_total {metrics['errors_total']}",
        "# HELP records_created_total Total prediction records stored",
        "# TYPE records_created_total counter",
        f"records_created_total {metrics['records_created_total']}",
        "# HELP history_reads_total Total history read queries",
        "# TYPE history_reads_total counter",
        f"history_reads_total {metrics['history_reads_total']}",
        "# HELP request_duration_seconds Total request duration in seconds",
        "# TYPE request_duration_seconds summary",
        f"request_duration_seconds_sum {metrics['request_duration_seconds_sum']:.4f}",
        f"request_duration_seconds_count {metrics['request_duration_seconds_count']}",
    ]
    try:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt FROM predictions")
                cnt = cursor.fetchone()[0]
                lines.append("# HELP history_total_records Total records in predictions database")
                lines.append("# TYPE history_total_records gauge")
                lines.append(f"history_total_records {cnt}")
    except Exception:
        pass
    return "\n".join(lines) + "\n"
