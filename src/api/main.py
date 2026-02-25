"""FastAPI application for NotebookLM API."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from src import __version__
from src.config import get_settings
from src.core.exceptions import NotebookLMError, AuthenticationError
from src.api.routes import (
    notebooks_router,
    sources_router,
    studio_router,
    research_router,
    sharing_router,
    notes_router,
    health_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    logger.info(f"Starting {settings.app_name} v{__version__}")
    
    # Verify authentication on startup
    try:
        from src.core import get_client
        client = get_client()
        logger.info("NotebookLM client initialized successfully")
    except AuthenticationError as e:
        logger.warning(f"Authentication not configured: {e}")
        logger.warning("Please run 'nlm login' to authenticate")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    REST API for Google NotebookLM.
    
    This API provides programmatic access to NotebookLM features:
    - Notebook management (create, list, delete)
    - Source management (add URLs, text, files)
    - AI-powered querying
    - Studio content generation (audio, video, reports)
    - Research operations
    - Sharing and collaboration
    - Notes management
    
    ## Authentication
    
    The API requires authentication with NotebookLM. Run `nlm login` first.
    
    ## Rate Limiting
    
    API requests are rate-limited to prevent abuse.
    """,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(NotebookLMError)
async def notebooklm_error_handler(request: Request, exc: NotebookLMError) -> JSONResponse:
    """Handle NotebookLM errors."""
    status_code = 500
    if isinstance(exc, AuthenticationError):
        status_code = 401
    elif "not found" in exc.message.lower():
        status_code = 404
    elif "validation" in exc.code.lower():
        status_code = 400
    
    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
            }
        },
    )


# API Key middleware (optional)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@app.middleware("http")
async def check_api_key(request: Request, call_next):
    """Check API key if configured."""
    if settings.api_key:
        # Skip health endpoints
        if request.url.path in ["/health", "/ready", "/live", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid or missing API key",
                    }
                },
            )
    
    return await call_next(request)


# Include routers
app.include_router(health_router)
app.include_router(notebooks_router)
app.include_router(sources_router)
app.include_router(studio_router)
app.include_router(research_router)
app.include_router(sharing_router)
app.include_router(notes_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


def run():
    """Run the API server."""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
