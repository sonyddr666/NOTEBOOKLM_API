"""Source management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, SourceError
from src.api.schemas.sources import (
    SourceCreate,
    SourceResponse,
    SourceListResponse,
    SourceAddResponse,
    SourceDeleteResponse,
    SourceSyncResponse,
)

router = APIRouter(prefix="/api/v1/notebooks", tags=["Sources"])


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


@router.get("/{notebook_id}/sources", response_model=SourceListResponse)
async def list_sources(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """List all sources in a notebook."""
    try:
        sources = client.list_sources(notebook_id)
        return SourceListResponse(
            notebook_id=notebook_id,
            sources=[SourceResponse(**s) for s in sources],
            count=len(sources),
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/sources", response_model=SourceAddResponse, status_code=201)
async def add_source(
    notebook_id: str,
    data: SourceCreate,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Add a source to a notebook."""
    try:
        result = {}
        
        if data.type == "url":
            if not data.url:
                raise HTTPException(status_code=400, detail="url is required for type=url")
            result = client.add_url_source(notebook_id, data.url)
            
        elif data.type == "text":
            if not data.text:
                raise HTTPException(status_code=400, detail="text is required for type=text")
            result = client.add_text_source(notebook_id, data.text, title=data.title or "")
            
        elif data.type == "drive":
            if not data.drive_id:
                raise HTTPException(status_code=400, detail="drive_id is required for type=drive")
            result = client.add_drive_source(
                notebook_id, 
                data.drive_id, 
                drive_type=data.drive_type or "document"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown source type: {data.type}")
        
        return SourceAddResponse(
            source_id=result.get("id", result.get("source_id", "")),
            title=result.get("title", ""),
            message="Source added successfully",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/sources/upload", response_model=SourceAddResponse, status_code=201)
async def upload_source(
    notebook_id: str,
    file: UploadFile = File(...),
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Upload a file as a source."""
    try:
        # Read file content
        content = await file.read()
        
        # Upload the file
        result = client.client.upload_file(
            notebook_id=notebook_id,
            filename=file.filename,
            content=content,
        )
        
        return SourceAddResponse(
            source_id=result.get("id", result.get("source_id", "")),
            title=file.filename or "Uploaded file",
            message="File uploaded successfully",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notebook_id}/sources/{source_id}", response_model=SourceDeleteResponse)
async def delete_source(
    notebook_id: str,
    source_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Delete a source from a notebook."""
    try:
        client.delete_source(notebook_id, source_id)
        return SourceDeleteResponse(message=f"Source {source_id} deleted successfully")
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except SourceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/sources/{source_id}/sync", response_model=SourceSyncResponse)
async def sync_drive_source(
    notebook_id: str,
    source_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Sync a Google Drive source with latest content."""
    try:
        client.sync_drive_source(notebook_id, source_id)
        return SourceSyncResponse(
            source_id=source_id,
            message="Source synced successfully",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except SourceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/sources/{source_id}/guide")
async def get_source_guide(
    notebook_id: str,
    source_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get AI-generated guide for a source."""
    try:
        result = client.client.get_source_guide(notebook_id, source_id)
        return {
            "source_id": source_id,
            "guide": result,
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/sources/{source_id}/fulltext")
async def get_source_fulltext(
    notebook_id: str,
    source_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get full text content of a source."""
    try:
        result = client.client.get_source_fulltext(notebook_id, source_id)
        return {
            "source_id": source_id,
            "fulltext": result,
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
