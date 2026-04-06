from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .models import AccessRole, LeakScanResult, SecretDetail, ShareToken, TokenRequest, TokenResponse, TokenValidationResponse, UploadResponse
from .storage import PermissionError, SecretStore
from encryption.crypto import AESCipher

app = FastAPI(
    title="SafeGuard Env Backend",
    description="Secure environment variable vault with AES-256 encryption, token-based sharing, versioning, and leak detection.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cipher = AESCipher.from_env()
store = SecretStore(cipher=cipher)


def resolve_role(role_header: str | None) -> AccessRole:
    if not role_header:
        return AccessRole.viewer
    try:
        return AccessRole(role_header.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role header. Use admin, editor, or viewer.")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "SafeGuard Env Backend"}


@app.post("/upload-env", response_model=UploadResponse)
async def upload_env(file: UploadFile = File(...), x_access_role: str | None = Header(None, alias="X-Access-Role")) -> UploadResponse:
    role = resolve_role(x_access_role)
    try:
        store.authorize(AccessRole.editor, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    raw_text = (await file.read()).decode("utf-8", errors="ignore")
    count = store.parse_env_content(raw_text)
    return UploadResponse(accepted_secrets=count, processed=len(raw_text.splitlines()), message=f"Stored {count} encrypted secret(s) successfully.")


@app.get("/secrets")
async def list_secrets(x_access_role: str | None = Header(None, alias="X-Access-Role")) -> list:
    role = resolve_role(x_access_role)
    try:
        store.authorize(AccessRole.viewer, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return [preview.model_dump() for preview in store.list_previews()]


@app.get("/secrets/{secret_name}")
async def secret_detail(secret_name: str, x_access_role: str | None = Header(None, alias="X-Access-Role")) -> SecretDetail:
    role = resolve_role(x_access_role)
    try:
        store.authorize(AccessRole.viewer, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    try:
        return store.get_detail(secret_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/reveal/{secret_name}")
async def reveal_secret(secret_name: str, version: int | None = None, x_access_role: str | None = Header(None, alias="X-Access-Role"), x_share_token: str | None = Header(None, alias="X-Share-Token")) -> dict:
    role = resolve_role(x_access_role)
    if x_share_token:
        try:
            token = store.validate_token(x_share_token)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        if token.secret_name != secret_name:
            raise HTTPException(status_code=403, detail="Share token does not grant access to this secret.")
        role = token.role

    try:
        store.authorize(AccessRole.editor, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    try:
        value = store.reveal_secret(secret_name, version)
        return {"secret_name": secret_name, "value": value, "version": version or "latest"}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/share-token", response_model=TokenResponse)
async def create_token(request: TokenRequest, x_access_role: str | None = Header(None, alias="X-Access-Role")) -> TokenResponse:
    role = resolve_role(x_access_role)
    try:
        store.authorize(AccessRole.admin, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    try:
        token = store.create_share_token(request.secret_name, request.role, request.ttl_seconds)
        return TokenResponse(
            secret_name=token.secret_name,
            role=token.role,
            token=token.token,
            expires_at=token.expires_at,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(x_share_token: str = Header(..., alias="X-Share-Token")) -> TokenValidationResponse:
    try:
        token = store.validate_token(x_share_token)
        return TokenValidationResponse(
            token=token.token,
            valid=True,
            secret_name=token.secret_name,
            role=token.role,
            expires_at=token.expires_at,
        )
    except PermissionError:
        return TokenValidationResponse(token=x_share_token, valid=False, secret_name=None, role=None, expires_at=None)


@app.post("/scan-leak", response_model=LeakScanResult)
async def scan_leak(file: UploadFile = File(...), x_access_role: str | None = Header(None, alias="X-Access-Role")) -> LeakScanResult:
    role = resolve_role(x_access_role)
    try:
        store.authorize(AccessRole.viewer, role)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    raw_text = (await file.read()).decode("utf-8", errors="ignore")
    return store.scan_text(raw_text)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
