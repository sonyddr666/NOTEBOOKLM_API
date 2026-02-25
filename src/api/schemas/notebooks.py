"""Pydantic schemas for notebook endpoints."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================

class NotebookCreate(BaseModel):
    """Request model for creating a notebook."""
    title: str = Field(default="", max_length=500, description="Notebook title")


class NotebookUpdate(BaseModel):
    """Request model for updating a notebook."""
    title: str = Field(..., max_length=500, description="New notebook title")


class QueryRequest(BaseModel):
    """Request model for querying a notebook."""
    query: str = Field(..., min_length=1, max_length=10000, description="Question to ask")
    source_ids: Optional[list[str]] = Field(default=None, description="Specific source IDs to query")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for follow-up questions")


class ChatConfigRequest(BaseModel):
    """Request model for configuring chat settings."""
    goal: str = Field(default="default", description="Chat goal: default, learning_guide, or custom")
    custom_prompt: Optional[str] = Field(default=None, max_length=10000, description="Custom prompt when goal=custom")
    response_length: str = Field(default="default", description="Response length: default, longer, shorter")


# ============================================================================
# Response Models
# ============================================================================

class NotebookResponse(BaseModel):
    """Response model for a single notebook."""
    id: str
    title: str
    source_count: int = 0
    url: str
    ownership: str = "mine"
    is_shared: bool = False
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class NotebookListResponse(BaseModel):
    """Response model for listing notebooks."""
    notebooks: list[NotebookResponse]
    count: int
    owned_count: int = 0
    shared_count: int = 0


class SourceInfo(BaseModel):
    """Source info in notebook details."""
    id: str
    title: str
    type: Optional[str] = None


class NotebookDetailResponse(BaseModel):
    """Response model for notebook details."""
    id: str
    title: str
    source_count: int = 0
    url: str
    sources: list[SourceInfo] = []


class NotebookSummaryResponse(BaseModel):
    """Response model for notebook summary."""
    summary: str
    suggested_topics: list[str] = []


class QueryResponse(BaseModel):
    """Response model for notebook query."""
    answer: str
    conversation_id: Optional[str] = None
    sources_used: list = []
    citations: dict = {}


class NotebookCreateResponse(BaseModel):
    """Response model for notebook creation."""
    id: str
    title: str
    url: str
    message: str = "Notebook created successfully"


class NotebookDeleteResponse(BaseModel):
    """Response model for notebook deletion."""
    message: str = "Notebook deleted successfully"


class ChatConfigResponse(BaseModel):
    """Response model for chat configuration."""
    notebook_id: str
    goal: str
    response_length: str
    message: str = "Chat settings updated"
