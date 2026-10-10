"""
Fireflies Clone — FastAPI Backend
Main application entry point with CORS, routers, and database initialization.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import Meeting, TranscriptSegment, Summary, ActionItem, Tag
from app.routers import meetings, action_items, search, ask_fred
from app.seed import seed_database

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fireflies Clone API",
    description="Meeting Notes & Transcription Platform API",
    version="1.0.0",
)

# CORS configuration — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(meetings.router)
app.include_router(action_items.router)
app.include_router(search.router)
app.include_router(ask_fred.router)

import os
from fastapi.staticfiles import StaticFiles

# Mount uploads directory for video playback
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.on_event("startup")
def on_startup():
    """Seed database on first run."""
    seed_database()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "fireflies-clone-api"}


@app.get("/api/ping")
def ping():
    """Ultra-lightweight ping for cron jobs."""
    return "ok"


@app.get("/api/tags")
def list_tags():
    """List all available tags."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        tags = db.query(Tag).all()
        return [{"id": t.id, "name": t.name, "color": t.color} for t in tags]
    finally:
        db.close()
