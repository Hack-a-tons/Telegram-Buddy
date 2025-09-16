from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

from .api.routes import router

load_dotenv()

app = FastAPI(
    title="Telegram Buddy AI",
    description="AI agent for developer conversations",
    version="1.0.0"
)

# Include API routes
app.include_router(router, prefix="/api")

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main HTML interface"""
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "telegram-buddy-ai"}
