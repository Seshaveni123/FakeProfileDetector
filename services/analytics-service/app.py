"""Analytics service. Reads history solely through the History Service API."""
import os
from collections import Counter

import httpx
from fastapi import FastAPI, HTTPException

HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://history-service:8001").rstrip("/")
TIMEOUT = float(os.getenv("HISTORY_REQUEST_TIMEOUT_SECONDS", "5"))
app = FastAPI(title="FakeGuard Analytics Service", version="2.0.0")


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
