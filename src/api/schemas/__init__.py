"""Pydantic schemas for API request/response models."""

from .notebooks import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
    NotebookListResponse,
    NotebookDetailResponse,
    NotebookSummaryResponse,
    QueryRequest,
    QueryResponse,
)
from .sources import (
    SourceCreate,
    SourceResponse,
    SourceListResponse,
)
from .studio import (
    AudioCreateRequest,
    VideoCreateRequest,
    ReportCreateRequest,
    SlideDeckCreateRequest,
    MindMapCreateRequest,
    StudioStatusResponse,
    ArtifactResponse,
)

__all__ = [
    # Notebooks
    "NotebookCreate",
    "NotebookUpdate",
    "NotebookResponse",
    "NotebookListResponse",
    "NotebookDetailResponse",
    "NotebookSummaryResponse",
    "QueryRequest",
    "QueryResponse",
    # Sources
    "SourceCreate",
    "SourceResponse",
    "SourceListResponse",
    # Studio
    "AudioCreateRequest",
    "VideoCreateRequest",
    "ReportCreateRequest",
    "SlideDeckCreateRequest",
    "MindMapCreateRequest",
    "StudioStatusResponse",
    "ArtifactResponse",
]
