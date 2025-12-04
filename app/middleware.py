from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeaders(BaseHTTPMiddleware):
    """
    Adds security-related HTTP headers to all responses.

    Headers added:
    - X-Content-Type-Options: Prevents MIME-sniffing
    - X-Frame-Options: Prevents clickjacking
    - Referrer-Policy: Controls referrer information
    - Content-Security-Policy: Restricts resource loading
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        headers = response.headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )

        return response


class CacheControl(BaseHTTPMiddleware):
    """
    Adds Cache-Control headers to static assets.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        path = request.url.path
        if path.endswith((".css", ".js", ".png", ".svg", ".ico", ".woff2")):
            # Cache for 1 week
            response.headers["Cache-Control"] = "public, max-age=604800, immutable"

        return response


# Type aliases
ClientIP = str
RequestTimestamps = list[datetime]


class RateLimit(BaseHTTPMiddleware):
    """
    Limits the number of requests per client IP within a sliding time window.

    Returns HTTP 429 (Too Many Requests) when limit is exceeded.

    Args:
        app: The FastAPI application instance.
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.max_requests = 100
        self.time_window = timedelta(seconds=60)
        self.request_log: dict[ClientIP, RequestTimestamps] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        current_time = datetime.now(timezone.utc)
        client_ip = request.client.host if request.client else "unknown"

        request_timestamps = self.request_log[client_ip]

        window_start = current_time - self.time_window
        request_timestamps[:] = [
            timestamp for timestamp in request_timestamps if timestamp > window_start
        ]

        request_timestamps.append(current_time)

        if len(request_timestamps) > self.max_requests:
            return Response(
                content="Too many requests",
                status_code=429,
                headers={"Retry-After": str(int(self.time_window.total_seconds()))},
            )

        return await call_next(request)
