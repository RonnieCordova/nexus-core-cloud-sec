import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas import AwsAccountCreate
from app.services.aws_scanner import verify_aws_access


router = APIRouter(prefix="/aws-accounts", tags=["aws-accounts"])


@router.post("")
def create_aws_account(payload: AwsAccountCreate, user: dict = Depends(get_current_user)):
    external_id = f"{settings.aws_external_id_prefix}-{user['tenant_id']}-{secrets.token_hex(8)}"

    with get_db() as conn:
        exists = conn.execute(
            "SELECT id FROM aws_accounts WHERE tenant_id = ? AND account_id = ?",
            (user["tenant_id"], payload.account_id),
        ).fetchone()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This AWS account is already registered for the tenant",
            )

        cur = conn.execute(
            """
            INSERT INTO aws_accounts(tenant_id, account_name, account_id, role_arn, external_id, regions)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user["tenant_id"],
                payload.account_name,
                payload.account_id,
                payload.role_arn,
                external_id,
                ",".join(payload.regions),
            ),
        )

    return {
        "id": cur.lastrowid,
        "account_name": payload.account_name,
        "account_id": payload.account_id,
        "role_arn": payload.role_arn,
        "external_id": external_id,
        "regions": payload.regions,
    }


@router.post("/{aws_account_id}/verify")
def verify_aws_account(aws_account_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        account = conn.execute(
            "SELECT * FROM aws_accounts WHERE id = ? AND tenant_id = ?",
            (aws_account_id, user["tenant_id"]),
        ).fetchone()

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AWS account not found")

    try:
        verification = verify_aws_access(dict(account))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Verification failed: {exc}") from exc

    with get_db() as conn:
        conn.execute(
            "UPDATE aws_accounts SET verified_at = ? WHERE id = ? AND tenant_id = ?",
            (datetime.now(timezone.utc).isoformat(), aws_account_id, user["tenant_id"]),
        )

    return verification


@router.get("")
def list_aws_accounts(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, account_name, account_id, role_arn, external_id, regions, verified_at, created_at
            FROM aws_accounts
            WHERE tenant_id = ?
            """,
            (user["tenant_id"],),
        ).fetchall()

    return [dict(r) for r in rows]
