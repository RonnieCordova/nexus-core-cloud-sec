from fastapi import APIRouter, HTTPException, status

from app.core.db import get_db
from app.core.security import generate_token, hash_password, verify_password
from app.schemas import AuthResponse, LoginRequest, SignupRequest


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    salt, password_hash = hash_password(payload.password)

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        tenant_cur = conn.execute("INSERT INTO tenants(name) VALUES (?)", (payload.tenant_name,))
        tenant_id = tenant_cur.lastrowid

        user_cur = conn.execute(
            "INSERT INTO users(tenant_id, email, password_salt, password_hash) VALUES (?, ?, ?, ?)",
            (tenant_id, payload.email.lower(), salt, password_hash),
        )
        user_id = user_cur.lastrowid

        token, token_hash, expires_at = generate_token()
        conn.execute(
            "INSERT INTO tokens(user_id, token_hash, expires_at) VALUES (?, ?, ?)",
            (user_id, token_hash, expires_at),
        )

    return AuthResponse(access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, password_salt, password_hash FROM users WHERE email = ?",
            (payload.email.lower(),),
        ).fetchone()

        if not user or not verify_password(payload.password, user["password_salt"], user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token, token_hash, expires_at = generate_token()
        conn.execute(
            "INSERT INTO tokens(user_id, token_hash, expires_at) VALUES (?, ?, ?)",
            (user["id"], token_hash, expires_at),
        )

    return AuthResponse(access_token=token)
