import secrets
import time
from typing import Dict, List, Optional

from .models import (
    AccessRole,
    LeakScanResult,
    SecretDetail,
    SecretPreview,
    SecretVersion,
    ShareToken,
)
from encryption.crypto import AESCipher, mask_value


class PermissionError(Exception):
    pass


class SecretStore:
    """In-memory secret vault with versioning, risk scoring, and token sharing."""

    ROLE_HIERARCHY = {
        AccessRole.viewer: 1,
        AccessRole.editor: 2,
        AccessRole.admin: 3,
    }

    def __init__(self, cipher: Optional[AESCipher] = None):
        self.cipher = cipher or AESCipher.from_env()
        self.secrets: Dict[str, List[SecretVersion]] = {}
        self.tokens: Dict[str, ShareToken] = {}

    def _compute_risk_score(self, name: str, value: str) -> str:
        score = 0
        normalized = name.upper()

        if any(keyword in normalized for keyword in ["SECRET", "PASSWORD", "API_KEY", "TOKEN", "ACCESS_KEY", "AWS", "GITHUB"]):
            score += 3
        if len(value) >= 32:
            score += 1
        if any(keyword in normalized for keyword in ["EMAIL", "ID", "USERNAME"]):
            score += 1
        if any(keyword in normalized for keyword in ["DEBUG", "TEST", "DEV"]):
            score -= 1

        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    def _scan_github_leaks(self, value: str) -> List[str]:
        warnings: List[str] = []
        pat = value.upper()
        if "GITHUB_TOKEN" in pat or "GH_TOKEN" in pat:
            warnings.append("possible GitHub token exposure")
        if "HTTP://" in value or "HTTPS://" in value:
            warnings.append("URL-like secret content")
        if "@" in value and ".com" in value:
            warnings.append("possible email / credential leak")
        return warnings

    def add_secret(self, name: str, value: str) -> SecretVersion:
        now = time.time()
        encrypted_value = self.cipher.encrypt(value)
        leak_flags = self._scan_github_leaks(value)
        risk_score = self._compute_risk_score(name, value)

        version_list = self.secrets.setdefault(name, [])
        version_number = len(version_list) + 1
        secret_version = SecretVersion(
            version=version_number,
            encrypted_value=encrypted_value,
            created_at=now,
            risk_score=risk_score,
            leak_flags=leak_flags,
        )
        version_list.append(secret_version)
        return secret_version

    def parse_env_content(self, env_text: str) -> int:
        accepted = 0
        for line in env_text.splitlines():
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue
            if "=" not in clean_line:
                continue
            name, value = clean_line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name and value:
                self.add_secret(name, value)
                accepted += 1
        return accepted

    def list_previews(self) -> List[SecretPreview]:
        previews: List[SecretPreview] = []
        for name, versions in self.secrets.items():
            latest = versions[-1]
            previews.append(
                SecretPreview(
                    name=name,
                    masked_value=mask_value(self.cipher.decrypt(latest.encrypted_value)),
                    current_version=latest.version,
                    version_count=len(versions),
                    risk_score=latest.risk_score,
                    leak_flags=latest.leak_flags,
                )
            )
        return previews

    def get_detail(self, name: str) -> SecretDetail:
        if name not in self.secrets:
            raise KeyError(f"Secret not found: {name}")
        versions = self.secrets[name]
        latest = versions[-1]
        return SecretDetail(
            name=name,
            masked_value=mask_value(self.cipher.decrypt(latest.encrypted_value)),
            current_version=latest.version,
            encrypted_versions=versions,
            risk_score=latest.risk_score,
            leak_flags=latest.leak_flags,
        )

    def reveal_secret(self, name: str, version: Optional[int] = None) -> str:
        if name not in self.secrets:
            raise KeyError(f"Secret not found: {name}")
        versions = self.secrets[name]
        chosen = versions[-1] if version is None else next((v for v in versions if v.version == version), None)
        if chosen is None:
            raise KeyError(f"Secret version not found: {version}")
        return self.cipher.decrypt(chosen.encrypted_value)

    def create_share_token(self, secret_name: str, role: AccessRole, ttl_seconds: int = 3600) -> ShareToken:
        if secret_name not in self.secrets:
            raise KeyError(f"Secret not found: {secret_name}")
        token_value = secrets.token_urlsafe(24)
        expires_at = time.time() + ttl_seconds
        token = ShareToken(token=token_value, secret_name=secret_name, role=role, expires_at=expires_at)
        self.tokens[token_value] = token
        return token

    def validate_token(self, token: str) -> ShareToken:
        if token not in self.tokens:
            raise PermissionError("Invalid share token")
        token_obj = self.tokens[token]
        if token_obj.expires_at < time.time():
            raise PermissionError("Share token expired")
        return token_obj

    def authorize(self, required_role: AccessRole, provided_role: AccessRole) -> None:
        if self.ROLE_HIERARCHY[provided_role] < self.ROLE_HIERARCHY[required_role]:
            raise PermissionError(f"Insufficient role privileges: {provided_role}")

    def scan_text(self, env_text: str) -> LeakScanResult:
        findings: List[str] = []
        if ".env" in env_text:
            findings.append("Referenced .env file path or leak")
        if "GITHUB_TOKEN" in env_text.upper() or "GH_TOKEN" in env_text.upper():
            findings.append("GitHub token pattern detected")
        if "API_KEY" in env_text.upper() and "SECRET" in env_text.upper():
            findings.append("High-risk API key and secret pattern")

        summary = "low"
        if len(findings) >= 2:
            summary = "high"
        elif len(findings) == 1:
            summary = "medium"

        return LeakScanResult(
            github_leak_cases=findings,
            risk_summary=summary,
            details="Simple pattern-based detection for GitHub and .env exposure.",
        )

    def clear(self) -> None:
        self.secrets.clear()
        self.tokens.clear()
