import httpx
import logging
from fastapi import Header, HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

async def verify_hcaptcha(captcha_token: str | None) -> bool:
    if not settings.CAPTCHA_ENABLED:
        return True
        
    if not captcha_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing CAPTCHA token"
        )
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://hcaptcha.com/siteverify",
                data={
                    "secret": settings.HCAPTCHA_SECRET,
                    "response": captcha_token
                }
            )
            result = response.json()
            if not result.get("success"):
                logger.warning(f"hCaptcha verification failed: {result}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Invalid CAPTCHA token"
                )
            return True
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with hCaptcha API: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Could not verify CAPTCHA"
            )

async def verify_captcha_header(x_captcha_token: str | None = Header(None, alias="X-Captcha-Token")):
    """
    FastAPI Dependency to verify hCaptcha token via X-Captcha-Token header.
    Only strictly enforces if settings.CAPTCHA_ENABLED is True.
    """
    return await verify_hcaptcha(x_captcha_token)
