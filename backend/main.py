"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import events, alerts, patrols, summaries, cameras, copmap, rag, llm, realtime_alerts
from backend.security import rate_limiter
from backend.exceptions import AppError, RateLimitError
from config.settings import get_settings
from database import create_db_engine, init_db

log = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    engine = create_db_engine(settings.database_url)
    init_db(engine)
    app.state.engine = engine
    app.state.settings = settings
    yield
    log.info("Shutting down...")


app = FastAPI(
    title=settings.api_title,
    description="""
## Overview
REST API for police patrol management, event detection, and intelligent alerting.

## Authentication
All endpoints require an API key passed via `X-API-Key` header.

## Rate Limiting
- 100 requests per minute per client
- `X-RateLimit-Remaining` header shows remaining quota
""",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)


@app.middleware("http")
async def request_tracking(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    start = datetime.now(timezone.utc)
    
    if not rate_limiter.check(request):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded", "error_code": "RATE_LIMITED"},
            headers={"Retry-After": "60", "X-Request-ID": request_id},
        )
    
    response = await call_next(request)
    
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    response.headers["X-Request-ID"] = request_id
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(request))
    
    log.info(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "request_id": request_id,
            **exc.details,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    log.exception(f"[{request_id}] Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id,
        },
    )


# Routers
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(patrols.router, prefix="/api/v1/patrol", tags=["Patrol"])
app.include_router(summaries.router, prefix="/api/v1/summaries", tags=["Summaries"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])
app.include_router(copmap.router, prefix="/api/v1/copmap", tags=["CopMap"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(llm.router, prefix="/api/v1", tags=["LLM"])
app.include_router(realtime_alerts.router, prefix="/api/v1/realtime-alerts", tags=["Realtime Alerts"])


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.api_version,
    }


@app.get("/metrics", tags=["System"])
async def metrics():
    """Basic metrics endpoint."""
    import psutil
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "uptime_seconds": int((datetime.now(timezone.utc) - app.state.start_time).total_seconds())
        if hasattr(app.state, "start_time")
        else 0,
    }


@app.get("/api/v1", tags=["System"])
async def api_info():
    """API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }
