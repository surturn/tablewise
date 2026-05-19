import pytest
from app.tasks import send_sms_notification, generate_inventory_forecast
from app.config import settings


def test_mock_sms_task():
    """Unit test: Verify the SMS Celery task executes its mock branch without crashing."""
    # Ensure we are testing the mock branch
    assert settings.AT_API_KEY == "mock_key"

    # Call the python function directly (bypassing the Celery @task decorator delay logic)
    result = send_sms_notification("0700000000", "Your order is ready!")

    assert result["status"] == "mock_success"
    assert result["phone"] == "0700000000"


def test_mock_ai_forecast_task(monkeypatch):
    """Unit test: Verify the AI Forecast Celery task executes its mock branch."""

    # Temporarily override the real API key with the expected mock string
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "mock_key")

    # Now this assertion will pass perfectly
    assert settings.OPENAI_API_KEY == "mock_key"

    result = generate_inventory_forecast("branch-uuid-123", "Sold 50 burgers yesterday.")

    assert result["currency"] == "USD"
    assert result["horizon_days"] == 7
    assert result["recommendations"][0]["confidence_score"] >= settings.AI_MIN_CONFIDENCE_SCORE
    assert result["data_quality_notes"]
