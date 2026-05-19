import hashlib

import bcrypt

BCRYPT_MAX_PASSWORD_BYTES = 72


def _bcrypt_password_bytes(password: str) -> bytes:
    """Return bcrypt-safe bytes while preserving full entropy for long passwords."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= BCRYPT_MAX_PASSWORD_BYTES:
        return password_bytes
    return hashlib.sha256(password_bytes).hexdigest().encode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against the hashed version.
    """
    return bcrypt.checkpw(_bcrypt_password_bytes(plain_password), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """
    Generates a bcrypt hash for a plaintext password.
    """
    return bcrypt.hashpw(_bcrypt_password_bytes(password), bcrypt.gensalt()).decode("utf-8")
