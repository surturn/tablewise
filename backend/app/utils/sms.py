import logging
import africastalking
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Africa's Talking
africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
sms_service = africastalking.SMS

async def send_sms_async(phone_number: str, message: str) -> bool:
    """
    Sends an SMS using Africa's Talking. 
    In development mode, it acts as a stub to save credits.
    Note: For heavy production loads, this should be dispatched to a Celery worker.
    """
    try:
        if settings.ENVIRONMENT == "development":
            logger.info(f"[STUB SMS] To {phone_number}: {message}")
            return True
            
        # Call Africa's Talking SDK synchronously. 
        # In a fully optimized flow, we will offload this to Celery.
        response = sms_service.send(message, [phone_number])
        logger.info(f"SMS sent successfully: {response}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}. Error: {str(e)}")
        return False