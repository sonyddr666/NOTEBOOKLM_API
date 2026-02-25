"""Pydantic schemas for studio endpoints."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================

class AudioCreateRequest(BaseModel):
    """Request model for creating an audio overview."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    audio_format: str = Field(default="deep_dive", description="Format: deep_dive, overview, etc.")
    audio_length: str = Field(default="default", description="Length: default, shorter, longer")
    language: str = Field(default="en", description="Language code")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class VideoCreateRequest(BaseModel):
    """Request model for creating a video overview."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    video_format: str = Field(default="explainer", description="Format: explainer, etc.")
    visual_style: str = Field(default="auto_select", description="Visual style")
    language: str = Field(default="en", description="Language code")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class InfographicCreateRequest(BaseModel):
    """Request model for creating an infographic."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    orientation: str = Field(default="landscape", description="Orientation: landscape, portrait")
    detail_level: str = Field(default="standard", description="Detail level: standard, detailed")
    language: str = Field(default="en", description="Language code")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class SlideDeckCreateRequest(BaseModel):
    """Request model for creating a slide deck."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    slide_format: str = Field(default="detailed_deck", description="Format: detailed_deck, etc.")
    slide_length: str = Field(default="default", description="Length: default, shorter, longer")
    language: str = Field(default="en", description="Language code")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class ReportCreateRequest(BaseModel):
    """Request model for creating a report."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    report_format: str = Field(default="Briefing Doc", description="Report format")
    custom_prompt: str = Field(default="", description="Custom prompt")
    language: str = Field(default="en", description="Language code")


class FlashcardsCreateRequest(BaseModel):
    """Request model for creating flashcards."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class QuizCreateRequest(BaseModel):
    """Request model for creating a quiz."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    question_count: int = Field(default=5, ge=2, le=20, description="Number of questions")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    focus_prompt: str = Field(default="", description="Optional focus prompt")


class MindMapCreateRequest(BaseModel):
    """Request model for creating a mind map."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    title: str = Field(default="Mind Map", description="Mind map title")


class DataTableCreateRequest(BaseModel):
    """Request model for creating a data table."""
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    description: str = Field(..., description="Description of the data table to create")
    language: str = Field(default="en", description="Language code")


class StudioCreateRequest(BaseModel):
    """Unified request model for creating studio content."""
    artifact_type: Literal[
        "audio", "video", "infographic", "slide_deck", "report",
        "flashcards", "quiz", "mind_map", "data_table"
    ] = Field(..., description="Type of artifact to create")
    source_ids: Optional[list[str]] = Field(default=None, description="Source IDs to include")
    # Audio options
    audio_format: Optional[str] = Field(default="deep_dive")
    audio_length: Optional[str] = Field(default="default")
    # Video options
    video_format: Optional[str] = Field(default="explainer")
    visual_style: Optional[str] = Field(default="auto_select")
    # Infographic options
    orientation: Optional[str] = Field(default="landscape")
    detail_level: Optional[str] = Field(default="standard")
    # Slide deck options
    slide_format: Optional[str] = Field(default="detailed_deck")
    slide_length: Optional[str] = Field(default="default")
    # Report options
    report_format: Optional[str] = Field(default="Briefing Doc")
    custom_prompt: Optional[str] = Field(default="")
    # Flashcard/Quiz options
    difficulty: Optional[str] = Field(default="medium")
    question_count: Optional[int] = Field(default=5)
    # Mind map options
    title: Optional[str] = Field(default="Mind Map")
    # Data table options
    description: Optional[str] = Field(default="")
    # Shared options
    language: str = Field(default="en")
    focus_prompt: str = Field(default="")


# ============================================================================
# Response Models
# ============================================================================

class ArtifactResponse(BaseModel):
    """Response model for a studio artifact."""
    artifact_id: str
    artifact_type: str
    title: Optional[str] = None
    status: str = "in_progress"
    created_at: Optional[str] = None
    url: Optional[str] = None
    download_url: Optional[str] = None


class StudioCreateResponse(BaseModel):
    """Response model for creating studio content."""
    artifact_id: str
    artifact_type: str
    status: str = "in_progress"
    message: str = "Artifact creation started"


class StudioStatusResponse(BaseModel):
    """Response model for studio status."""
    notebook_id: str
    artifacts: list[ArtifactResponse]
    total: int
    completed: int
    in_progress: int


class ArtifactDeleteResponse(BaseModel):
    """Response model for deleting an artifact."""
    message: str = "Artifact deleted successfully"


class ArtifactRenameRequest(BaseModel):
    """Request model for renaming an artifact."""
    new_title: str = Field(..., max_length=500, description="New artifact title")


class ArtifactRenameResponse(BaseModel):
    """Response model for renaming an artifact."""
    artifact_id: str
    new_title: str
    message: str = "Artifact renamed successfully"


# ============================================================================
# Research Models
# ============================================================================

class ResearchStartRequest(BaseModel):
    """Request model for starting research."""
    query: str = Field(..., min_length=1, max_length=1000, description="Research query")
    research_type: Literal["fast", "deep"] = Field(default="fast", description="Research type")
    source_type: Literal["web", "drive"] = Field(default="web", description="Source type")


class ResearchStatusResponse(BaseModel):
    """Response model for research status."""
    research_id: str
    status: str
    progress: Optional[int] = None
    sources_found: Optional[int] = None
    sources: Optional[list[dict]] = None


class ResearchImportRequest(BaseModel):
    """Request model for importing research sources."""
    source_ids: Optional[list[str]] = Field(default=None, description="Specific source IDs to import")


class ResearchImportResponse(BaseModel):
    """Response model for importing research sources."""
    imported_count: int
    sources: list[dict]
    message: str = "Sources imported successfully"
