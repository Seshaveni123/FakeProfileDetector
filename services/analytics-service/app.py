import time
import os
from collections import Counter

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://history-service:8001").rstrip("/")
TIMEOUT = float(os.getenv("HISTORY_REQUEST_TIMEOUT_SECONDS", "5"))
app = FastAPI(title="FakeGuard Analytics Service", version="2.0.0")

metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "dashboard_requests_total": 0,
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


def all_predictions() -> list[dict]:
    offset, records = 0, []
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            while True:
                response = client.get(f"{HISTORY_SERVICE_URL}/history", params={"limit": 1000, "offset": offset})
                response.raise_for_status()
                page = response.json()
                records.extend(page["predictions"])
                offset += len(page["predictions"])
                if offset >= page["total"] or not page["predictions"]:
                    return records
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="History service is unavailable") from exc


@app.get("/")
def health():
    try:
        response = httpx.get(f"{HISTORY_SERVICE_URL}/", timeout=TIMEOUT)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="History service is unavailable") from exc
    return {"status": "ok", "service": "analytics"}


@app.get("/dashboard")
def dashboard():
    metrics["dashboard_requests_total"] += 1
    records = all_predictions()
    total = len(records)
    fake_count = sum(record["prediction"] == 1 for record in records)
    by_platform = {platform: [record for record in records if record["platform"] == platform] for platform in ("instagram", "twitter")}
    risk = Counter(record["risk_level"] for record in records)
    daily = {}
    for record in records:
        date = record["timestamp"][:10]
        entry = daily.setdefault(date, {"date": date, "total": 0, "fake": 0, "real_count": 0})
        entry["total"] += 1
        entry["fake" if record["prediction"] == 1 else "real_count"] += 1
    return {"total_scans": total, "fake_count": fake_count, "real_count": total - fake_count, "fake_percentage": round(fake_count / total * 100, 1) if total else 0, "avg_probability": round(sum(record["probability"] for record in records) / total, 4) if total else 0, "platform_breakdown": {platform: {"total": len(items), "fake": sum(item["prediction"] == 1 for item in items), "real": sum(item["prediction"] == 0 for item in items)} for platform, items in by_platform.items()}, "risk_distribution": {level: risk[level] for level in ("critical", "high", "medium", "low")}, "recent_predictions": records[:10], "daily_stats": sorted(daily.values(), key=lambda item: item["date"], reverse=True)[:7]}


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
        "# HELP dashboard_requests_total Total dashboard analytics requests",
        "# TYPE dashboard_requests_total counter",
        f"dashboard_requests_total {metrics['dashboard_requests_total']}",
        "# HELP request_duration_seconds Total request duration in seconds",
        "# TYPE request_duration_seconds summary",
        f"request_duration_seconds_sum {metrics['request_duration_seconds_sum']:.4f}",
        f"request_duration_seconds_count {metrics['request_duration_seconds_count']}",
    ]
    return "\n".join(lines) + "\n"
