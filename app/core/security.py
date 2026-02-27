import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone


TOKEN_TTL_HOURS = 24


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    real_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), real_salt, 120_000)
    return real_salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, password_hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    _, candidate = hash_password(password, salt=salt)
    return hmac.compare_digest(candidate, password_hash_hex)


def generate_token() -> tuple[str, str, str]:
    plain = secrets.token_urlsafe(32)
    token_hash = _hash_bytes(plain.encode("utf-8"))
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)).isoformat()
    return plain, token_hash, expires_at


def hash_token(token: str) -> str:
    return _hash_bytes(token.encode("utf-8"))
