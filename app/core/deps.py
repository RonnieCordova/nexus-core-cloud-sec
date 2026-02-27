from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.db import get_db
from app.core.security import hash_token


bearer = HTTPBearer(auto_error=True)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    token_hash = hash_token(credentials.credentials)

    with get_db() as conn:
        row = conn.execute(
            """
            SELECT t.id AS token_id, u.id as user_id, u.email, u.tenant_id, t.expires_at
            FROM tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token_hash = ?
            """,
            (token_hash,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        expires = datetime.fromisoformat(row["expires_at"])
        if expires < datetime.now(timezone.utc):
            conn.execute("DELETE FROM tokens WHERE id = ?", (row["token_id"],))
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return {"user_id": row["user_id"], "email": row["email"], "tenant_id": row["tenant_id"]}
