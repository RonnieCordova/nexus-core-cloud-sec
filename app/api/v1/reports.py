import json
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas import ScanReportOut


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{scan_id}", response_model=ScanReportOut)
def get_scan_report(scan_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        scan = conn.execute(
            "SELECT id, aws_account_id, status, summary_json FROM scans WHERE id = ? AND tenant_id = ?",
            (scan_id, user["tenant_id"]),
        ).fetchone()
        if not scan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan report not found")

        findings = conn.execute(
            "SELECT severity, service, resource_id, title, description FROM findings WHERE scan_id = ?",
            (scan_id,),
        ).fetchall()

    return ScanReportOut(
        scan_id=scan["id"],
        aws_account_id=scan["aws_account_id"],
        status=scan["status"],
        summary=json.loads(scan["summary_json"]),
        findings=[dict(row) for row in findings],
    )
