from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import settings
from .routers import auth, post, user, vote

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