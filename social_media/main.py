from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS
from . import models
from .routers import post, user, auth, vote
from .config import settings


app = FastAPI()

# --- CORS MIDDLEWARE SETUP ---
# This allows web browsers to talk to your server
origins = [
    "*", # "Wildcard": Allows ALL domains (Good for development)
    # "https://www.google.com", # In production, specific domains only
    # "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Allow all headers
)
# -----------------------------

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello World"}