"""Pydantic schemas for source endpoints."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# Request Models
# ============================================================================

class URLSourceCreate(BaseModel):
    """Request model for adding a URL source."""
    type: Literal["url"] = "url"
    url: str = Field(..., description="URL to add as source")


class TextSourceCreate(BaseModel):
    """Request model for adding a text source."""
    type: Literal["text"] = "text"
    text: str = Field(..., min_length=1, max_length=100000, description="Text content")
    title: Optional[str] = Field(default=None, max_length=500, description="Optional title")


class DriveSourceCreate(BaseModel):
    """Request model for adding a Google Drive source."""
    type: Literal["drive"] = "drive"
    drive_id: str = Field(..., description="Google Drive file ID")
    drive_type: str = Field(default="document", description="Type of drive document")


class FileSourceCreate(BaseModel):
    """Request model for file upload (metadata only, file uploaded separately)."""
    type: Literal["file"] = "file"
    filename: str = Field(..., description="Original filename")


class SourceCreate(BaseModel):
    """Unified request model for adding sources."""
    type: Literal["url", "text", "drive"] = Field(..., description="Source type")
    url: Optional[str] = Field(default=None, description="URL (for type=url)")
    text: Optional[str] = Field(default=None, description="Text content (for type=text)")
    title: Optional[str] = Field(default=None, description="Title (for type=text)")
    drive_id: Optional[str] = Field(default=None, description="Drive ID (for type=drive)")
    drive_type: Optional[str] = Field(default="document", description="Drive type (for type=drive)")


# ============================================================================
# Response Models
# ============================================================================

class SourceResponse(BaseModel):
    """Response model for a single source."""
    id: str
    title: str
    type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    url: Optional[str] = None


class SourceListResponse(BaseModel):
    """Response model for listing sources."""
    notebook_id: str
    sources: list[SourceResponse]
    count: int


class SourceAddResponse(BaseModel):
    """Response model for adding a source."""
    source_id: str
    title: str
    message: str = "Source added successfully"


class SourceDeleteResponse(BaseModel):
    """Response model for deleting a source."""
    message: str = "Source deleted successfully"


class SourceSyncResponse(BaseModel):
    """Response model for syncing a Drive source."""
    source_id: str
    message: str = "Source synced successfully"


class SourceFreshnessResponse(BaseModel):
    """Response model for source freshness check."""
    source_id: str
    is_stale: bool
    last_modified: Optional[str] = None
