"""Security utilities: API key auth, rate limiting, request tracking."""

import hashlib
import os
import time
import uuid
from collections import defaultdict
from functools import wraps
from typing import Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEYS = set(os.getenv("API_KEYS", "dev-key-123,test-key-456").split(","))


def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        api_key = request.headers.get("X-API-Key", "")
        client_ip = request.client.host if request.client else "unknown"
        return hashlib.md5(f"{api_key}:{client_ip}".encode()).hexdigest()[:16]
    
    def check(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        now = time.time()
        window_start = now - 60
        
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if ts > window_start
        ]
        
        if len(self.requests[client_id]) >= self.rpm:
            return False
        
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, request: Request) -> int:
        client_id = self._get_client_id(request)
        now = time.time()
        window_start = now - 60
        recent = [ts for ts in self.requests[client_id] if ts > window_start]
        return max(0, self.rpm - len(recent))


rate_limiter = RateLimiter(requests_per_minute=100)


async def rate_limit_middleware(request: Request, call_next):
    if not rate_limiter.check(request):
        return HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": "60"}
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(request))
    return response


def generate_request_id() -> str:
    return str(uuid.uuid4())[:8]


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def sanitize_string(value: str, max_length: int = 1000) -> str:
    if not value:
        return value
    value = value[:max_length]
    dangerous = ["<script", "javascript:", "onerror=", "onclick="]
    for pattern in dangerous:
        value = value.replace(pattern, "")
    return value.strip()
