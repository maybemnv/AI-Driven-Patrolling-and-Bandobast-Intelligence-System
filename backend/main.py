"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import events, alerts, patrols, summaries, cameras
from database import create_db_engine, init_db

log = logging.getLogger(__name__)


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
    description="REST API for police patrol management, event detection, and alert handling",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start).total_seconds()
    log.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )


app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(patrols.router, prefix="/api/v1/patrol", tags=["Patrol"])
app.include_router(summaries.router, prefix="/api/v1/summaries", tags=["Summaries"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1", tags=["System"])
async def api_info():
    return {
        "name": "Patrolling & Bandobast API",
        "version": "1.0.0",
        "endpoints": ["/events", "/alerts", "/patrol", "/summaries", "/cameras"]
    }
