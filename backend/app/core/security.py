from __future__ import annotations

import base64
import hmac
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import PlainTextResponse, Response

from app.core.config import Settings

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
PUBLIC_PATHS = {"/health", "/app.js", "/favicon.ico"}


def configure_security(app: FastAPI, settings: Settings) -> None:
    if settings.allowed_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        early_response = _validate_request(request, settings)
        if early_response is not None:
            _apply_security_headers(early_response)
            return early_response

        response = await call_next(request)
        _apply_security_headers(response)
        return response


def _validate_request(request: Request, settings: Settings) -> Response | None:
    size_response = _reject_oversized_request(request, settings)
    if size_response is not None:
        return size_response

    origin_response = _reject_cross_origin_write(request, settings)
    if origin_response is not None:
        return origin_response

    if settings.auth_enabled and not _is_public_path(request.url.path):
        if not _has_valid_credentials(request, settings):
            response = PlainTextResponse("Authentication required.", status_code=401)
            if settings.auth_username and settings.auth_password:
                response.headers["WWW-Authenticate"] = 'Basic realm="Attrition App"'
            else:
                response.headers["WWW-Authenticate"] = "Bearer"
            return response

    return None


def _is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS


def _reject_oversized_request(request: Request, settings: Settings) -> Response | None:
    content_length = request.headers.get("content-length")
    if not content_length:
        return None
    try:
        size = int(content_length)
    except ValueError:
        return PlainTextResponse("Invalid Content-Length header.", status_code=400)
    if size > settings.max_upload_bytes:
        return PlainTextResponse("Request body is too large.", status_code=413)
    return None


def _reject_cross_origin_write(request: Request, settings: Settings) -> Response | None:
    if request.method.upper() not in UNSAFE_METHODS:
        return None

    request_origin = _request_origin(request)
    if request_origin is None:
        return None

    allowed_origins = set(settings.allowed_origins)
    host = request.headers.get("host")
    if host:
        allowed_origins.add(f"http://{host}")
        allowed_origins.add(f"https://{host}")

    if request_origin.rstrip("/") not in {origin.rstrip("/") for origin in allowed_origins}:
        return PlainTextResponse("Cross-origin write rejected.", status_code=403)
    return None


def _request_origin(request: Request) -> str | None:
    origin = request.headers.get("origin")
    if origin:
        return origin

    referer = request.headers.get("referer")
    if not referer:
        return None

    parsed = urlsplit(referer)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _has_valid_credentials(request: Request, settings: Settings) -> bool:
    auth_header = request.headers.get("authorization", "")

    if settings.auth_token:
        bearer_prefix = "Bearer "
        if auth_header.startswith(bearer_prefix) and hmac.compare_digest(
            auth_header[len(bearer_prefix) :], settings.auth_token
        ):
            return True

        api_key = request.headers.get("x-api-key")
        if api_key and hmac.compare_digest(api_key, settings.auth_token):
            return True

    if settings.auth_username and settings.auth_password:
        basic_prefix = "Basic "
        if not auth_header.startswith(basic_prefix):
            return False
        try:
            decoded = base64.b64decode(auth_header[len(basic_prefix) :]).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return False
        username, separator, password = decoded.partition(":")
        if not separator:
            return False
        return hmac.compare_digest(username, settings.auth_username) and hmac.compare_digest(
            password, settings.auth_password
        )

    return False


def _apply_security_headers(response: Response) -> None:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=()",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
        "https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'",
    )
