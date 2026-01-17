"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os
import uuid

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from backend.routers import events, alerts, patrols, summaries, cameras
from backend.security import rate_limiter, verify_api_key
from database import create_db_engine, init_db

log = logging.getLogger(__name__)

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    engine = create_db_engine("sqlite:///./data/patrolling.db")
    init_db(engine)
    app.state.engine = engine
    yield
    log.info("Shutting down...")


app = FastAPI(
    title="AI-Driven Patrolling & Bandobast API",
    description="""
## Overview
REST API for police patrol management, event detection, and intelligent alerting.

## Authentication
All endpoints require an API key passed via `X-API-Key` header.

## Rate Limiting
- 100 requests per minute per client
- `X-RateLimit-Remaining` header shows remaining quota

## Error Codes
| Code | Description |
|------|-------------|
| 400 | Invalid request data |
| 401 | Missing API key |
| 403 | Invalid API key |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
""",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
            headers={"Retry-After": "60", "X-Request-ID": request_id}
        )
    
    response = await call_next(request)
    
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    response.headers["X-Request-ID"] = request_id
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(request))
    
    log.info(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    log.exception(f"[{request_id}] Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id
        }
    )


app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(patrols.router, prefix="/api/v1/patrol", tags=["Patrol"])
app.include_router(summaries.router, prefix="/api/v1/summaries", tags=["Summaries"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])


@app.get("/health", tags=["System"], summary="Health check", description="Returns API health status")
async def health_check():
    """Check if the API is running and healthy."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1", tags=["System"], summary="API info", description="Returns available endpoints")
async def api_info():
    """Get API version and available endpoints."""
    return {
        "name": "Patrolling & Bandobast API",
        "version": "1.0.0",
        "endpoints": ["/events", "/alerts", "/patrol", "/summaries", "/cameras"],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/v1/openapi.json", tags=["System"], include_in_schema=False)
async def get_openapi_spec():
    """Export OpenAPI specification as JSON."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )
