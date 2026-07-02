import pytest
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token, decode_access_token
from app.models.enums import UserRole


def test_password_hashing():
    """Unit test for password hashing utility."""
    password = "secure_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_creation_and_decoding():
    """Unit test for JWT token lifecycle."""
    subject = "user-uuid-123"
    role = UserRole.CASHIER
    outlet_id = "outlet-uuid-456"

    token = create_access_token(subject=subject, role=role, outlet_id=outlet_id)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == subject
    assert payload["role"] == role.value
    assert payload["outlet_id"] == outlet_id


def test_jwt_legacy_branch_id_kwarg():
    """Unit test: create_access_token still accepts the legacy branch_id kwarg and maps it to outlet_id."""
    token = create_access_token(subject="user-uuid-123", role=UserRole.CASHIER, branch_id="branch-uuid-456")

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["outlet_id"] == "branch-uuid-456"


def test_jwt_invalid_token():
    """Unit test for handling tampered JWTs."""
    payload = decode_access_token("invalid.token.here")
    assert payload is None