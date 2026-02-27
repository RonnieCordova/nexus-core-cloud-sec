import json
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas import ScanRequest
from app.services.aws_scanner import run_security_scan


router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("")
def execute_scan(payload: ScanRequest, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        account = conn.execute(
            "SELECT * FROM aws_accounts WHERE id = ? AND tenant_id = ?",
            (payload.aws_account_id, user["tenant_id"]),
        ).fetchone()

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AWS account not found")

    try:
        summary, findings = run_security_scan(dict(account))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Scan failed: {exc}") from exc

    with get_db() as conn:
        scan_cur = conn.execute(
            "INSERT INTO scans(tenant_id, aws_account_id, status, summary_json) VALUES (?, ?, ?, ?)",
            (user["tenant_id"], payload.aws_account_id, "completed", json.dumps(summary)),
        )
        scan_id = scan_cur.lastrowid

        for finding in findings:
            conn.execute(
                """
                INSERT INTO findings(scan_id, severity, service, resource_id, title, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    finding["severity"],
                    finding["service"],
                    finding["resource_id"],
                    finding["title"],
                    finding["description"],
                ),
            )

    return {"scan_id": scan_id, "status": "completed", "summary": summary, "findings_count": len(findings)}
