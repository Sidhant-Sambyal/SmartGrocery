import logging
import secrets
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Response, Request

from app.models.request_models import LoginRequest
from app.auth.email_validator import is_company_email
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# ── In-memory session store (keyed by session token) ─────────
# For production, replace with Redis or a database-backed store.
_sessions: dict[str, str] = {}   # token → email

SESSION_COOKIE = "sg_session"
COOKIE_MAX_AGE = 60 * 60 * 8     # 8 hours

# ── Rate limiter for login endpoint ──────────────────────────
# Max 3 attempts per 1-second window, tracked by client IP.
_LOGIN_MAX_ATTEMPTS = 3
_LOGIN_WINDOW_SECS = 1.0
_login_timestamps: dict[str, deque] = defaultdict(deque)


def _check_rate_limit(client_ip: str) -> None:
    """
    Raise HTTP 429 if *client_ip* has exceeded
    _LOGIN_MAX_ATTEMPTS within the last _LOGIN_WINDOW_SECS.
    """
    now = time.monotonic()
    timestamps = _login_timestamps[client_ip]

    # Discard timestamps outside the sliding window
    while timestamps and timestamps[0] <= now - _LOGIN_WINDOW_SECS:
        timestamps.popleft()

    if len(timestamps) >= _LOGIN_MAX_ATTEMPTS:
        logger.warning(
            "Rate limit exceeded for IP %s (%d attempts in %.1fs)",
            client_ip,
            len(timestamps),
            _LOGIN_WINDOW_SECS,
        )
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please wait a moment and try again.",
        )

    timestamps.append(now)


# ── GET /api/auth/domain — expose company domain to login page ─
@router.get("/domain")
def get_domain():
    return {"domain": settings.COMPANY_DOMAIN}


# ── POST /api/auth/login ──────────────────────────────────────
@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response):
    # Rate-limit by client IP
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    email = body.email.strip().lower()

    logger.info("Login attempt: %s", email)

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    if not is_company_email(email):
        logger.warning("Rejected login — not a company email: %s", email)
        raise HTTPException(
            status_code=403,
            detail="this email is not valid",
        )

    token = secrets.token_urlsafe(32)
    _sessions[token] = email

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )

    logger.info("Login successful: %s", email)
    return {"ok": True, "email": email}


# ── POST /api/auth/logout ─────────────────────────────────────
@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        _sessions.pop(token, None)

    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}


# ── GET /api/auth/me — check current session ─────────────────
@router.get("/me")
def me(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    email = _sessions.get(token) if token else None

    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    return {"email": email}
