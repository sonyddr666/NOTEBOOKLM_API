"""Research endpoints."""

from fastapi import APIRouter, HTTPException, Depends

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, ResearchError
from src.api.schemas.studio import (
    ResearchStartRequest,
    ResearchStatusResponse,
    ResearchImportRequest,
    ResearchImportResponse,
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/notebooks", tags=["Research"])


# New Deep Research request model
class DeepResearchRequest(BaseModel):
    """Request model for deep research."""
    topic: str
    mode: str = "fast"  # fast (~30s) or deep (~5min)
    source_type: str = "web"  # web or drive


class DeepResearchResponse(BaseModel):
    """Response model for deep research."""
    notebook_id: str
    notebook_title: str
    research_id: str
    status: str
    message: str


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


@router.post("/{notebook_id}/research/start", status_code=201)
async def start_research(
    notebook_id: str,
    data: ResearchStartRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Start a research operation."""
    try:
        result = client.start_research(
            notebook_id=notebook_id,
            query=data.query,
            research_type=data.research_type,
            source_type=data.source_type,
        )
        return {
            "research_id": result.get("research_id", ""),
            "status": "started",
            "query": data.query,
            "research_type": data.research_type,
            "message": "Research started",
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/research/{research_id}")
async def poll_research(
    notebook_id: str,
    research_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Poll research status and results."""
    try:
        result = client.poll_research(notebook_id, research_id)
        return {
            "research_id": research_id,
            "status": result.get("status", "unknown"),
            "progress": result.get("progress"),
            "sources_found": result.get("sources_found", 0),
            "sources": result.get("sources", []),
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except ResearchError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/research/{research_id}/import", response_model=ResearchImportResponse)
async def import_research_sources(
    notebook_id: str,
    research_id: str,
    data: ResearchImportRequest = None,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Import sources from research results."""
    try:
        source_ids = data.source_ids if data else None
        result = client.import_research_sources(
            notebook_id=notebook_id,
            research_id=research_id,
            source_ids=source_ids,
        )
        
        sources = result.get("sources", []) if result else []
        return ResearchImportResponse(
            imported_count=len(sources),
            sources=sources,
            message="Sources imported successfully",
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except ResearchError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Deep Research - Creates notebook and researches topic automatically
# =============================================================================

@router.post("/research/deep", response_model=DeepResearchResponse, status_code=201)
async def deep_research(
    data: DeepResearchRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """
    Start a deep research operation.
    
    This creates a new notebook with the topic as title and starts research
    to find relevant sources from the web or Google Drive.
    
    - **mode**: "fast" (~30 seconds, ~10 sources) or "deep" (~5 minutes, ~40 sources)
    - **source_type**: "web" (web search) or "drive" (Google Drive)
    
    Use the returned notebook_id and research_id to poll for results.
    """
    try:
        # Create notebook with topic as title
        notebook_title = data.topic
        notebook = client.create_notebook(title=notebook_title)
        notebook_id = notebook.get("id")
        
        if not notebook_id:
            raise HTTPException(status_code=500, detail="Failed to create notebook")
        
        # Start research on the new notebook
        result = client.start_research(
            notebook_id=notebook_id,
            query=data.topic,
            research_type=data.mode,  # fast or deep
            source_type=data.source_type,
        )
        
        research_id = result.get("research_id", "") or result.get("task_id", "")
        
        return DeepResearchResponse(
            notebook_id=notebook_id,
            notebook_title=notebook_title,
            research_id=research_id,
            status="started",
            message=f"Deep research started for '{data.topic}'. "
                   f"Mode: {data.mode}, Source: {data.source_type}. "
                   f"Use /notebooks/{{notebook_id}}/research/{{research_id}} to check progress."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
