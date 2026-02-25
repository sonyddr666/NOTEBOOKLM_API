"""API routes module."""

from .notebooks import router as notebooks_router
from .sources import router as sources_router
from .studio import router as studio_router
from .research import router as research_router
from .sharing import router as sharing_router
from .notes import router as notes_router
from .health import router as health_router

__all__ = [
    "notebooks_router",
    "sources_router",
    "studio_router",
    "research_router",
    "sharing_router",
    "notes_router",
    "health_router",
]
