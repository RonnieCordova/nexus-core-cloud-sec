from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.aws_accounts import router as aws_accounts_router
from app.api.v1.scans import router as scans_router
from app.api.v1.reports import router as reports_router


api_router = APIRouter(prefix="/v1")
api_router.include_router(auth_router)
api_router.include_router(aws_accounts_router)
api_router.include_router(scans_router)
api_router.include_router(reports_router)
