"""Notes endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, NoteError
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/notebooks", tags=["Notes"])


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


class NoteCreate(BaseModel):
    """Request model for creating a note."""
    title: str = Field(..., max_length=500, description="Note title")
    content: str = Field(default="", description="Note content")


class NoteUpdate(BaseModel):
    """Request model for updating a note."""
    title: Optional[str] = Field(default=None, max_length=500, description="New title")
    content: Optional[str] = Field(default=None, description="New content")


class NoteResponse(BaseModel):
    """Response model for a note."""
    id: str
    title: str
    content: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class NoteListResponse(BaseModel):
    """Response model for listing notes."""
    notebook_id: str
    notes: list[NoteResponse]
    count: int


@router.get("/{notebook_id}/notes", response_model=NoteListResponse)
async def list_notes(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """List all notes in a notebook."""
    try:
        notes = client.list_notes(notebook_id)
        return NoteListResponse(
            notebook_id=notebook_id,
            notes=[NoteResponse(**n) for n in notes],
            count=len(notes),
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    notebook_id: str,
    data: NoteCreate,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a note in a notebook."""
    try:
        result = client.create_note(notebook_id, data.title, content=data.content)
        return NoteResponse(
            id=result.get("id", result.get("note_id", "")),
            title=data.title,
            content=data.content,
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    notebook_id: str,
    note_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get a specific note."""
    try:
        notes = client.list_notes(notebook_id)
        note = next((n for n in notes if n.get("id") == note_id), None)
        
        if not note:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        
        return NoteResponse(**note)
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notebook_id}/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    notebook_id: str,
    note_id: str,
    data: NoteUpdate,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Update a note."""
    try:
        client.update_note(
            notebook_id, 
            note_id, 
            title=data.title, 
            content=data.content
        )
        
        # Get updated note
        notes = client.list_notes(notebook_id)
        note = next((n for n in notes if n.get("id") == note_id), None)
        
        return NoteResponse(
            id=note_id,
            title=note.get("title", data.title) if note else data.title,
            content=note.get("content", data.content) if note else data.content,
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except NoteError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notebook_id}/notes/{note_id}")
async def delete_note(
    notebook_id: str,
    note_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Delete a note."""
    try:
        client.delete_note(notebook_id, note_id)
        return {"message": f"Note {note_id} deleted successfully"}
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except NoteError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
