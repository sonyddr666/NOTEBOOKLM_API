"""Notebook endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, AuthenticationError
from src.api.schemas.notebooks import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
    NotebookListResponse,
    NotebookDetailResponse,
    NotebookSummaryResponse,
    NotebookCreateResponse,
    NotebookDeleteResponse,
    QueryRequest,
    QueryResponse,
    ChatConfigRequest,
    ChatConfigResponse,
    SourceInfo,
)

router = APIRouter(prefix="/api/v1/notebooks", tags=["Notebooks"])


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    max_results: int = 100,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """List all notebooks."""
    try:
        notebooks = client.list_notebooks(max_results=max_results)
        owned_count = sum(1 for nb in notebooks if nb.get("ownership") == "mine")
        shared_count = len(notebooks) - owned_count
        
        return NotebookListResponse(
            notebooks=[NotebookResponse(**nb) for nb in notebooks],
            count=len(notebooks),
            owned_count=owned_count,
            shared_count=shared_count,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=NotebookCreateResponse, status_code=201)
async def create_notebook(
    data: NotebookCreate,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Create a new notebook."""
    try:
        result = client.create_notebook(title=data.title)
        return NotebookCreateResponse(
            id=result["id"],
            title=result["title"],
            url=result["url"],
            message="Notebook created successfully",
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}", response_model=NotebookDetailResponse)
async def get_notebook(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get notebook details."""
    try:
        nb = client.get_notebook(notebook_id)
        sources = client.list_sources(notebook_id)
        
        return NotebookDetailResponse(
            id=nb["id"],
            title=nb["title"],
            source_count=nb.get("source_count", len(sources)),
            url=nb["url"],
            sources=[SourceInfo(**s) for s in sources],
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def rename_notebook(
    notebook_id: str,
    data: NotebookUpdate,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Rename a notebook."""
    try:
        client.rename_notebook(notebook_id, data.title)
        nb = client.get_notebook(notebook_id)
        return NotebookResponse(**nb)
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notebook_id}", response_model=NotebookDeleteResponse)
async def delete_notebook(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Delete a notebook."""
    try:
        client.delete_notebook(notebook_id)
        return NotebookDeleteResponse(message=f"Notebook {notebook_id} deleted successfully")
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/summary", response_model=NotebookSummaryResponse)
async def get_notebook_summary(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get AI-generated notebook summary."""
    try:
        result = client.get_notebook_summary(notebook_id)
        return NotebookSummaryResponse(**result)
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/query", response_model=QueryResponse)
async def query_notebook(
    notebook_id: str,
    data: QueryRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Query a notebook with AI."""
    try:
        result = client.query(
            notebook_id=notebook_id,
            query_text=data.query,
            source_ids=data.source_ids,
            conversation_id=data.conversation_id,
        )
        return QueryResponse(**result)
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/chat-config", response_model=ChatConfigResponse)
async def configure_chat(
    notebook_id: str,
    data: ChatConfigRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Configure notebook chat settings."""
    try:
        # Validate goal
        valid_goals = ("default", "learning_guide", "custom")
        if data.goal not in valid_goals:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid goal. Must be one of: {', '.join(valid_goals)}"
            )
        
        # Validate response_length
        valid_lengths = ("default", "longer", "shorter")
        if data.response_length not in valid_lengths:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid response_length. Must be one of: {', '.join(valid_lengths)}"
            )
        
        # Validate custom_prompt when goal=custom
        if data.goal == "custom" and not data.custom_prompt:
            raise HTTPException(
                status_code=400,
                detail="custom_prompt is required when goal is 'custom'"
            )
        
        client.client.configure_chat(
            notebook_id=notebook_id,
            goal=data.goal,
            custom_prompt=data.custom_prompt,
            response_length=data.response_length,
        )
        
        return ChatConfigResponse(
            notebook_id=notebook_id,
            goal=data.goal,
            response_length=data.response_length,
            message="Chat settings updated",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
