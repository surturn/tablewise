import logging
import re
import africastalking
from app.config import settings

logger = logging.getLogger(__name__)
africastalking.initialize(settings.AFRICASTALKING_USERNAME or settings.AT_USERNAME, settings.AFRICASTALKING_API_KEY or settings.AT_API_KEY)
sms_service = africastalking.SMS


def normalize_south_sudan_phone(phone_number: str) -> str:
    digits = re.sub(r"\D", "", phone_number)
    if digits.startswith("211"):
        return f"+{digits}"
    if digits.startswith("0"):
        return f"+211{digits[1:]}"
    if len(digits) == 9:
        return f"+211{digits}"
    if phone_number.startswith("+"):
        return phone_number
    return f"+{digits}"


async def send_sms_async(phone_number: str, message: str) -> bool:
    try:
        formatted_phone = normalize_south_sudan_phone(phone_number)
        branded_message = message.replace("TableWise", "GrandPlatform")
        if settings.ENVIRONMENT == "development":
            logger.info("[STUB SMS] To %s: %s", formatted_phone, branded_message)
            return True
        response = sms_service.send(branded_message, [formatted_phone])
        logger.info("SMS sent successfully: %s", response)
        return True
    except Exception as e:
        logger.error("Failed to send SMS to %s. Error: %s", phone_number, str(e))
        return False
