"""Prometheus metrics middleware for API monitoring."""
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

if PROMETHEUS_AVAILABLE:
    insight_requests_total = Counter(
        "insight_requests_total", "Total API requests", ["method", "endpoint"]
    )
    insight_request_duration = Histogram(
        "insight_request_duration_seconds", "API request duration", ["method", "endpoint"]
    )
    insight_errors_total = Counter(
        "insight_errors_total", "Total API errors", ["method", "endpoint"]
    )


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not PROMETHEUS_AVAILABLE:
            return await call_next(request)

        start = time.time()
        endpoint = request.url.path
        method = request.method
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                insight_errors_total.labels(method=method, endpoint=endpoint).inc()
            return response
        except Exception:
            insight_errors_total.labels(method=method, endpoint=endpoint).inc()
            raise
        finally:
            duration = time.time() - start
            insight_requests_total.labels(method=method, endpoint=endpoint).inc()
            insight_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def metrics_response() -> Response:
    if not PROMETHEUS_AVAILABLE:
        return Response(content="# prometheus_client not installed\n", media_type="text/plain")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
