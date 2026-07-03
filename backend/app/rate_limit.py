from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Redis-backed so the limit is shared across API replicas (Render can run more
# than one). Falls back to in-process memory when REDIS_URL isn't configured
# (e.g. local unit tests), trading cross-replica accuracy for zero setup cost.
_storage_uri = settings.REDIS_URL or "memory://"

limiter = Limiter(key_func=get_remote_address, storage_uri=_storage_uri)
