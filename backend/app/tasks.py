import json
import logging

import africastalking
from openai import OpenAI
from app.celery_worker import celery_app
from app.config import settings
from app.services.ai_validation import validate_inventory_forecast

logger = logging.getLogger(__name__)

# Initialize Africa's Talking
africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
sms_service = africastalking.SMS


@celery_app.task(name="send_sms_notification", bind=True, max_retries=3)
def send_sms_notification(self, phone_number: str, message: str):
    """
    Background task to send an SMS. Retries up to 3 times if it fails.
    """
    try:
        if settings.ENVIRONMENT == "development" and settings.AT_API_KEY == "mock_key":
            logger.info(f"[CELERY MOCK SMS] To {phone_number}: {message}")
            return {"status": "mock_success", "phone": phone_number}

        response = sms_service.send(message, [phone_number])
        logger.info(f"SMS Sent: {response}")
        return response
    except Exception as exc:
        logger.error(f"Failed to send SMS to {phone_number}. Retrying...")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="generate_inventory_forecast")
def generate_inventory_forecast(branch_id: str, historical_data_summary: str):
    """
    Background task calling OpenAI to analyze sales data and recommend re-orders.
    """
    try:
        if settings.ENVIRONMENT == "development" and settings.OPENAI_API_KEY == "mock_key":
            logger.info(f"[CELERY MOCK AI] Generating forecast for branch {branch_id}")
            forecast = validate_inventory_forecast({
                "branch_id": branch_id,
                "horizon_days": 7,
                "currency": "USD",
                "recommendations": [
                    {
                        "item_name": "Bottled water",
                        "recommended_quantity": 120,
                        "unit": "bottles",
                        "confidence_score": 0.82,
                        "reason": "Bookings and prior weekend demand indicate higher guest consumption."
                    }
                ],
                "data_quality_notes": ["Mock development forecast; production uses validated order, booking, and inventory data."],
            })
            return forecast.model_dump()

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        Based on the following validated sales, booking, and inventory summary for outlet ID {branch_id}:
        {historical_data_summary}

        Return JSON only with: branch_id, horizon_days, currency=USD, recommendations, and data_quality_notes.
        Each recommendation needs item_name, recommended_quantity, unit, confidence_score from 0 to 1, and reason.
        Flag insufficient or suspicious source data in data_quality_notes instead of inventing values.
        """

        # Using the sync client inside Celery
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You are a hospitality inventory analyst for a hotel, restaurant, and bar in Juba, South Sudan. Validate source data and never invent measurements."},
                {"role": "user", "content": prompt}
            ]
        )

        forecast_payload = json.loads(response.choices[0].message.content or "{}")
        forecast = validate_inventory_forecast(forecast_payload)
        return forecast.model_dump()
    except Exception as exc:
        logger.error(f"OpenAI API call failed: {exc}")
        return f"AI Forecasting temporarily unavailable: {str(exc)}"