import logging
import africastalking
from openai import OpenAI
from app.celery_worker import celery_app
from app.config import settings

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
            return "Mock AI Suggestion: Stock up on 20kg of Maize Flour and 10L of Cooking Oil for the weekend."

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        Based on the following historical sales data summary for branch ID {branch_id}:
        {historical_data_summary}

        Provide a concise, bulleted re-order list predicting demand for the next 7 days.
        Consider local Kenyan consumption patterns (e.g., weekends, month-end).
        """

        # Using the sync client inside Celery
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Can be upgraded to gpt-4 or gpt-4o if needed
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You are an expert restaurant inventory manager in Kenya."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
    except Exception as exc:
        logger.error(f"OpenAI API call failed: {exc}")
        return f"AI Forecasting temporarily unavailable: {str(exc)}"