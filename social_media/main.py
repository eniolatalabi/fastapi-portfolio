import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from . import models
from .config import settings
from .limiter import limiter
from .routers import auth, post, user, vote

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("social_media")

app = FastAPI(
    title="Social Media API",
    description="JWT-authenticated CRUD API with posts, votes, and "
                "object-level authorization.",
)

# Origins come from configuration, never a wildcard: browsers reject
# wildcard origins combined with credentials, and an explicit allowlist
# is the correct trust boundary in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """One structured line per request: method, path, status, duration.

    Unhandled exceptions are logged with a stack trace before FastAPI
    turns them into a 500, so production failures are never silent.
    """
    start = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled error on %s %s",
                         request.method, request.url.path)
        raise
    duration_ms = (perf_counter() - start) * 1000
    logger.info("%s %s -> %s %.1fms", request.method, request.url.path,
                response.status_code, duration_ms)
    return response


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"service": "Social Media API", "status": "online", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    """Liveness probe for the deployment platform."""
    return {"status": "healthy"}