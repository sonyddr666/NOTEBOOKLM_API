"""Sharing endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.core import get_client, NotebookLMClientWrapper, NotebookNotFoundError, ShareError
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/notebooks", tags=["Sharing"])


def get_notebook_client() -> NotebookLMClientWrapper:
    """Dependency to get the NotebookLM client."""
    return get_client()


class PublicAccessRequest(BaseModel):
    """Request model for setting public access."""
    public: bool = Field(..., description="True to enable, False to disable")


class CollaboratorRequest(BaseModel):
    """Request model for adding a collaborator."""
    email: str = Field(..., description="Collaborator email address")
    role: str = Field(default="reader", description="Role: reader or writer")


class ShareStatusResponse(BaseModel):
    """Response model for share status."""
    notebook_id: str
    is_public: bool
    public_url: Optional[str] = None
    collaborators: list = []


@router.get("/{notebook_id}/share", response_model=ShareStatusResponse)
async def get_share_status(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Get sharing status of a notebook."""
    try:
        result = client.get_share_status(notebook_id)
        return ShareStatusResponse(
            notebook_id=notebook_id,
            is_public=result.get("is_public", False),
            public_url=result.get("public_url"),
            collaborators=result.get("collaborators", []),
        )
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/share/public")
async def enable_public_access(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Enable public access to a notebook."""
    try:
        client.set_public_access(notebook_id, public=True)
        result = client.get_share_status(notebook_id)
        return {
            "notebook_id": notebook_id,
            "is_public": True,
            "public_url": result.get("public_url"),
            "message": "Public access enabled",
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except ShareError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notebook_id}/share/public")
async def disable_public_access(
    notebook_id: str,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Disable public access to a notebook."""
    try:
        client.set_public_access(notebook_id, public=False)
        return {
            "notebook_id": notebook_id,
            "is_public": False,
            "message": "Public access disabled",
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except ShareError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/share/collaborator")
async def add_collaborator(
    notebook_id: str,
    data: CollaboratorRequest,
    client: NotebookLMClientWrapper = Depends(get_notebook_client),
):
    """Add a collaborator to a notebook."""
    try:
        # Validate role
        valid_roles = ("reader", "writer")
        if data.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        client.add_collaborator(notebook_id, data.email, role=data.role)
        return {
            "notebook_id": notebook_id,
            "email": data.email,
            "role": data.role,
            "message": f"Collaborator {data.email} added as {data.role}",
        }
    except NotebookNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_id} not found")
    except ShareError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
