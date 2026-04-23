"""
VeriClip AI API - FastAPI Application Entry Point
Handles lifespan, CORS, health checks, and route registration.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.routes import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for startup and shutdown events."""
    # Startup
    print("🛡️  VeriClip AI API starting...")
    print(f"📍 Region: {settings.GOOGLE_CLOUD_REGION}")
    print(f"🔗 Docs: http://localhost:8000/docs")
    yield
    # Shutdown
    print("🛡️  VeriClip AI API shutting down...")


app = FastAPI(
    title="VeriClip AI API",
    version="0.2.0",
    description="Autonomous agent swarm that identifies, tracks, and flags unauthorized usage of sports media with <5-second detection.",
    lifespan=lifespan,
)

# CORS middleware - allow all origins for easy deployment to Vercel/Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code, "path": request.url.path},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors without leaking internal details."""
    print(f"Unhandled exception: {exc}")  # Server-side logging
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500, "path": request.url.path},
    )


# Register all routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
