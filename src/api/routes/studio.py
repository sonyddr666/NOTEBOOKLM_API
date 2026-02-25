"""Studio content endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, StudioError
from src.api.schemas.studio import (
    AudioCreateRequest,
    VideoCreateRequest,
    ReportCreateRequest,
    SlideDeckCreateRequest,
    MindMapCreateRequest,
    StudioCreateRequest,
    StudioCreateResponse,
    StudioStatusResponse,
    ArtifactResponse,
    ArtifactDeleteResponse,
    ArtifactRenameRequest,
    ArtifactRenameResponse,
)

router = APIRouter(prefix="/api/v1/notebooks", tags=["Studio"])


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


@router.post("/{notebook_id}/studio/audio", response_model=StudioCreateResponse, status_code=201)
async def create_audio(
    notebook_id: str,
    data: AudioCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create an audio overview (podcast)."""
    try:
        result = client.create_audio_overview(
            notebook_id=notebook_id,
            source_ids=data.source_ids,
            audio_format=data.audio_format,
            audio_length=data.audio_length,
            language=data.language,
            focus_prompt=data.focus_prompt,
        )
        return StudioCreateResponse(
            artifact_id=result.get("artifact_id", ""),
            artifact_type="audio",
            status=result.get("status", "in_progress"),
            message="Audio overview generation started",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/studio/video", response_model=StudioCreateResponse, status_code=201)
async def create_video(
    notebook_id: str,
    data: VideoCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a video overview."""
    try:
        result = client.create_video_overview(
            notebook_id=notebook_id,
            source_ids=data.source_ids,
            video_format=data.video_format,
            visual_style=data.visual_style,
            language=data.language,
            focus_prompt=data.focus_prompt,
        )
        return StudioCreateResponse(
            artifact_id=result.get("artifact_id", ""),
            artifact_type="video",
            status=result.get("status", "in_progress"),
            message="Video overview generation started",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/studio/report", response_model=StudioCreateResponse, status_code=201)
async def create_report(
    notebook_id: str,
    data: ReportCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a report."""
    try:
        result = client.create_report(
            notebook_id=notebook_id,
            source_ids=data.source_ids,
            report_format=data.report_format,
            custom_prompt=data.custom_prompt,
            language=data.language,
        )
        return StudioCreateResponse(
            artifact_id=result.get("artifact_id", ""),
            artifact_type="report",
            status=result.get("status", "in_progress"),
            message="Report generation started",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/studio/slide-deck", response_model=StudioCreateResponse, status_code=201)
async def create_slide_deck(
    notebook_id: str,
    data: SlideDeckCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a slide deck."""
    try:
        result = client.create_slide_deck(
            notebook_id=notebook_id,
            source_ids=data.source_ids,
            slide_format=data.slide_format,
            slide_length=data.slide_length,
            language=data.language,
            focus_prompt=data.focus_prompt,
        )
        return StudioCreateResponse(
            artifact_id=result.get("artifact_id", ""),
            artifact_type="slide_deck",
            status=result.get("status", "in_progress"),
            message="Slide deck generation started",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/studio/mind-map", response_model=StudioCreateResponse, status_code=201)
async def create_mind_map(
    notebook_id: str,
    data: MindMapCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a mind map."""
    try:
        result = client.create_mind_map(
            notebook_id=notebook_id,
            source_ids=data.source_ids,
            title=data.title,
        )
        return StudioCreateResponse(
            artifact_id=result.get("mind_map_id", result.get("artifact_id", "")),
            artifact_type="mind_map",
            status="completed",
            message="Mind map created successfully",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/studio", response_model=StudioCreateResponse, status_code=201)
async def create_studio_content(
    notebook_id: str,
    data: StudioCreateRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create studio content (unified endpoint)."""
    try:
        result = {}
        
        if data.artifact_type == "audio":
            result = client.create_audio_overview(
                notebook_id=notebook_id,
                source_ids=data.source_ids,
                audio_format=data.audio_format or "deep_dive",
                audio_length=data.audio_length or "default",
                language=data.language,
                focus_prompt=data.focus_prompt,
            )
        elif data.artifact_type == "video":
            result = client.create_video_overview(
                notebook_id=notebook_id,
                source_ids=data.source_ids,
                video_format=data.video_format or "explainer",
                visual_style=data.visual_style or "auto_select",
                language=data.language,
                focus_prompt=data.focus_prompt,
            )
        elif data.artifact_type == "report":
            result = client.create_report(
                notebook_id=notebook_id,
                source_ids=data.source_ids,
                report_format=data.report_format or "Briefing Doc",
                custom_prompt=data.custom_prompt or "",
                language=data.language,
            )
        elif data.artifact_type == "slide_deck":
            result = client.create_slide_deck(
                notebook_id=notebook_id,
                source_ids=data.source_ids,
                slide_format=data.slide_format or "detailed_deck",
                slide_length=data.slide_length or "default",
                language=data.language,
                focus_prompt=data.focus_prompt,
            )
        elif data.artifact_type == "mind_map":
            result = client.create_mind_map(
                notebook_id=notebook_id,
                source_ids=data.source_ids,
                title=data.title or "Mind Map",
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported artifact type: {data.artifact_type}"
            )
        
        return StudioCreateResponse(
            artifact_id=result.get("artifact_id", result.get("mind_map_id", "")),
            artifact_type=data.artifact_type,
            status=result.get("status", "in_progress"),
            message=f"{data.artifact_type} creation started",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/studio/status", response_model=StudioStatusResponse)
async def get_studio_status(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get status of all studio artifacts."""
    try:
        artifacts = client.get_studio_status(notebook_id)
        
        completed = [a for a in artifacts if a.get("status") == "completed"]
        in_progress = [a for a in artifacts if a.get("status") == "in_progress"]
        
        return StudioStatusResponse(
            notebook_id=notebook_id,
            artifacts=[ArtifactResponse(**a) for a in artifacts],
            total=len(artifacts),
            completed=len(completed),
            in_progress=len(in_progress),
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get artifact details."""
    try:
        artifacts = client.get_studio_status(notebook_id)
        artifact = next((a for a in artifacts if a.get("artifact_id") == artifact_id), None)
        
        if not artifact:
            raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")
        
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: str,
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get download URL for an artifact."""
    try:
        result = client.client.download_artifact(artifact_id, notebook_id=notebook_id)
        return {
            "artifact_id": artifact_id,
            "download_url": result.get("download_url") if result else None,
            "status": result.get("status") if result else "unknown",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/artifacts/{artifact_id}", response_model=ArtifactDeleteResponse)
async def delete_artifact(
    artifact_id: str,
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Delete a studio artifact."""
    try:
        client.client.delete_studio_artifact(artifact_id, notebook_id=notebook_id)
        return ArtifactDeleteResponse(message=f"Artifact {artifact_id} deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/artifacts/{artifact_id}/rename", response_model=ArtifactRenameResponse)
async def rename_artifact(
    artifact_id: str,
    data: ArtifactRenameRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Rename a studio artifact."""
    try:
        client.client.rename_studio_artifact(artifact_id, data.new_title)
        return ArtifactRenameResponse(
            artifact_id=artifact_id,
            new_title=data.new_title,
            message="Artifact renamed successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
