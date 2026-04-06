from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AccessRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class SecretVersion(BaseModel):
    version: int
    encrypted_value: str
    created_at: float
    risk_score: str
    leak_flags: List[str] = Field(default_factory=list)


class SecretPreview(BaseModel):
    name: str
    masked_value: str
    current_version: int
    version_count: int
    risk_score: str
    leak_flags: List[str] = Field(default_factory=list)


class ShareToken(BaseModel):
    token: str
    secret_name: str
    role: AccessRole
    expires_at: float


class UploadResponse(BaseModel):
    accepted_secrets: int
    processed: int
    message: str


class LeakScanResult(BaseModel):
    github_leak_cases: List[str]
    risk_summary: str
    details: Optional[str] = None


class TokenRequest(BaseModel):
    secret_name: str
    role: AccessRole = AccessRole.viewer
    ttl_seconds: int = 3600


class TokenResponse(BaseModel):
    secret_name: str
    role: AccessRole
    token: str
    expires_at: float


class TokenValidationResponse(BaseModel):
    token: str
    valid: bool
    secret_name: Optional[str]
    role: Optional[AccessRole]
    expires_at: Optional[float]


class SecretDetail(BaseModel):
    name: str
    masked_value: str
    current_version: int
    encrypted_versions: List[SecretVersion]
    risk_score: str
    leak_flags: List[str]
