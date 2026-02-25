"""Health check endpoints."""

from fastapi import APIRouter

from src import __version__

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "notebooklm-api",
        "version": __version__,
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    from src.core import get_client
    
    try:
        client = get_client()
        # Try a simple operation to verify auth
        client.list_notebooks(max_results=1)
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}
