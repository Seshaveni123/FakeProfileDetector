"""Unit tests for dashboard aggregation without a running History Service."""
import importlib.util
from pathlib import Path


def load_analytics_service():
    path = Path(__file__).parents[1] / "services" / "analytics-service" / "app.py"
    spec = importlib.util.spec_from_file_location("analytics_service_app", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dashboard_counts_low_risk_records(monkeypatch):
    service = load_analytics_service()
    record = {
        "timestamp": "2026-10-15T10:00:00+00:00",
        "platform": "instagram",
        "prediction": 0,
        "probability": 0.12,
        "risk_level": "low",
    }
    monkeypatch.setattr(service, "all_predictions", lambda: [record])

    dashboard = service.dashboard()

    assert dashboard["recent_predictions"] == [record]
    assert dashboard["risk_distribution"]["low"] == 1
    assert dashboard["real_count"] == 1
