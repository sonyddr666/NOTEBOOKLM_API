"""Research endpoints."""

from fastapi import APIRouter, HTTPException, Depends

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, ResearchError
from src.api.schemas.studio import (
    ResearchStartRequest,
    ResearchStatusResponse,
    ResearchImportRequest,
    ResearchImportResponse,
)

router = APIRouter(prefix="/api/v1/notebooks", tags=["Research"])


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
