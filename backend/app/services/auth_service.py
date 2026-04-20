from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.security import verify_password


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Checks the database for a user with the given email and verifies the password.
    Returns the User object if successful, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user