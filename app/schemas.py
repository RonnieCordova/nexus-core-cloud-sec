from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AwsAccountCreate(BaseModel):
    account_name: str = Field(min_length=2, max_length=120)
    account_id: str = Field(pattern=r"^\d{12}$")
    role_arn: str = Field(min_length=20, max_length=255)
    regions: list[str] = Field(default_factory=lambda: ["us-east-1"])


class ScanRequest(BaseModel):
    aws_account_id: int


class FindingOut(BaseModel):
    severity: str
    service: str
    resource_id: str
    title: str
    description: str


class ScanReportOut(BaseModel):
    scan_id: int
    aws_account_id: int
    status: str
    summary: dict
    findings: list[FindingOut]
