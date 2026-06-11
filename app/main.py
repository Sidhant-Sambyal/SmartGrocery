import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.grocery import router as grocery_router
from app.api.auth import router as auth_router, _sessions, SESSION_COOKIE
from app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

_frontend = Path(__file__).parent.parent / "frontend"

app = FastAPI(
    title="Smart Grocery API",
    description="AI-powered grocery item classifier backed by Gemini.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging ───────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled exception: %s %s", request.method, request.url.path)
        raise
    ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s → %s (%.2fms)", request.method, request.url.path, response.status_code, ms)
    return response


# ── Auth guard middleware ─────────────────────────────────────
@app.middleware("http")
async def auth_guard(request: Request, call_next):
    path = request.url.path

    # Always allow: login page, auth API, static assets
    public = (
        path == "/login"
        or path == "/login.html"
        or path.startswith("/api/auth/")
        or path.startswith("/api/health")
        or "." in path.split("/")[-1]   # any file with extension (css, js, etc.)
    )

    if not public:
        token = request.cookies.get(SESSION_COOKIE)
        if not (token and token in _sessions):
            return RedirectResponse(url="/login", status_code=302)

    return await call_next(request)


# ── API routes ────────────────────────────────────────────────
app.include_router(grocery_router, prefix="/api")
app.include_router(auth_router,   prefix="/api/auth")


# ── Named pages (before StaticFiles mount) ────────────────────
@app.get("/login")
def login_page():
    return FileResponse(str(_frontend / "login.html"))


@app.get("/api/health")
def health():
    return {"status": "healthy"}


# ── Frontend static files (mounted LAST) ─────────────────────
app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
