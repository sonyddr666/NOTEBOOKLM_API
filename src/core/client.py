"""NotebookLM client wrapper for API and Bot usage."""

import logging
from pathlib import Path
from typing import Optional, Any
from contextlib import contextmanager

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.errors import ClientAuthenticationError

from src.config import get_settings
from .exceptions import AuthenticationError, NotebookNotFoundError

logger = logging.getLogger(__name__)


class NotebookLMClientWrapper:
    """Wrapper around NotebookLMClient with error handling and convenience methods."""
    
    def __init__(self, profile: str = None):
        """Initialize the client wrapper.
        
        Args:
            profile: Optional profile name for multi-account support
        """
        self.settings = get_settings()
        self.profile = profile or self.settings.notebooklm_profile
        self._client: Optional[NotebookLMClient] = None
    
    def _get_cookies_path(self) -> Path:
        """Get the path to the cookies file for the current profile."""
        return self.settings.notebooklm_data_dir / f"cookies_{self.profile}.json"
    
    def _load_cookies(self) -> dict[str, str]:
        """Load cookies from the auth file.
        
        Returns:
            Cookie dict for authentication
            
        Raises:
            AuthenticationError: If cookies cannot be loaded
        """
        cookies_path = self._get_cookies_path()
        
        if not cookies_path.exists():
            # Try default cookies file
            default_path = self.settings.notebooklm_data_dir / "cookies.json"
            if default_path.exists():
                cookies_path = default_path
            else:
                raise AuthenticationError(
                    f"No authentication found. Please run 'nlm login' first. "
                    f"Expected cookies at: {cookies_path}"
                )
        
        try:
            import json
            with open(cookies_path, 'r') as f:
                data = json.load(f)
            
            # Handle different cookie formats
            if isinstance(data, dict):
                # If it's already a dict of cookie name -> value
                if 'cookies' in data:
                    # Might be nested format
                    cookies_data = data['cookies']
                    if isinstance(cookies_data, dict):
                        return cookies_data
                    elif isinstance(cookies_data, str):
                        # Parse cookie string into dict
                        return self._parse_cookie_string(cookies_data)
                elif 'raw' in data:
                    return self._parse_cookie_string(data['raw'])
                else:
                    # Assume it's already a dict of cookie name -> value
                    return data
            elif isinstance(data, str):
                return self._parse_cookie_string(data)
            elif isinstance(data, list):
                # List of cookie dicts
                result = {}
                for item in data:
                    if isinstance(item, dict) and 'name' in item and 'value' in item:
                        result[item['name']] = item['value']
                return result
            else:
                raise AuthenticationError(f"Unknown cookie format in {cookies_path}")
                
        except json.JSONDecodeError as e:
            raise AuthenticationError(f"Invalid cookie file format: {e}")
        except Exception as e:
            raise AuthenticationError(f"Failed to load cookies: {e}")
    
    def _parse_cookie_string(self, cookie_str: str) -> dict[str, str]:
        """Parse a cookie string into a dict.
        
        Args:
            cookie_str: Cookie string like "name1=value1; name2=value2"
            
        Returns:
            Dict of cookie name -> value
        """
        result = {}
        for part in cookie_str.split(';'):
            part = part.strip()
            if '=' in part:
                name, value = part.split('=', 1)
                result[name.strip()] = value.strip()
        return result
    
    def _create_client(self) -> NotebookLMClient:
        """Create a new NotebookLMClient instance.
        
        Returns:
            Authenticated NotebookLMClient
            
        Raises:
            AuthenticationError: If client cannot be authenticated
        """
        try:
            cookies = self._load_cookies()
            client = NotebookLMClient(cookies=cookies)
            return client
        except ClientAuthenticationError as e:
            raise AuthenticationError(f"Authentication failed: {e}")
        except Exception as e:
            raise AuthenticationError(f"Failed to create client: {e}")
    
    @property
    def client(self) -> NotebookLMClient:
        """Get or create the NotebookLM client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def refresh(self) -> None:
        """Refresh the client by reloading cookies."""
        self._client = None
        _ = self.client  # Force re-initialization
    
    def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
    
    # =========================================================================
    # Notebook Operations
    # =========================================================================
    
    def list_notebooks(self, max_results: int = 100) -> list[dict]:
        """List all notebooks.
        
        Args:
            max_results: Maximum number of notebooks to return
            
        Returns:
            List of notebook dictionaries
        """
        notebooks = self.client.list_notebooks()
        return [
            {
                "id": nb.id,
                "title": nb.title,
                "source_count": nb.source_count,
                "url": nb.url,
                "ownership": nb.ownership,
                "is_shared": nb.is_shared,
                "created_at": nb.created_at,
                "modified_at": nb.modified_at,
            }
            for nb in notebooks[:max_results]
        ]
    
    def get_notebook(self, notebook_id: str) -> dict:
        """Get notebook details.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            Notebook details dictionary
            
        Raises:
            NotebookNotFoundError: If notebook doesn't exist
        """
        try:
            nb = self.client.get_notebook(notebook_id)
            if not nb:
                raise NotebookNotFoundError(notebook_id)
            
            # Handle different response formats
            if hasattr(nb, 'id'):
                return {
                    "id": nb.id,
                    "title": getattr(nb, 'title', 'Untitled'),
                    "source_count": getattr(nb, 'source_count', 0),
                    "url": getattr(nb, 'url', f"https://notebooklm.google.com/notebook/{nb.id}"),
                }
            elif isinstance(nb, list) and nb:
                data = nb[0] if isinstance(nb[0], list) else nb
                if isinstance(data, list) and len(data) >= 3:
                    return {
                        "id": data[2] if len(data) > 2 else notebook_id,
                        "title": data[0] if isinstance(data[0], str) else "Untitled",
                        "source_count": len(data[1]) if len(data) > 1 and isinstance(data[1], list) else 0,
                        "url": f"https://notebooklm.google.com/notebook/{notebook_id}",
                    }
            
            raise NotebookNotFoundError(notebook_id)
            
        except NotebookNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get notebook {notebook_id}: {e}")
            raise NotebookNotFoundError(notebook_id)
    
    def create_notebook(self, title: str = "") -> dict:
        """Create a new notebook.
        
        Args:
            title: Optional notebook title
            
        Returns:
            Created notebook details
        """
        nb = self.client.create_notebook(title)
        if nb and hasattr(nb, 'id'):
            return {
                "id": nb.id,
                "title": nb.title,
                "url": nb.url,
            }
        raise Exception("Failed to create notebook")
    
    def rename_notebook(self, notebook_id: str, new_title: str) -> bool:
        """Rename a notebook.
        
        Args:
            notebook_id: Notebook UUID
            new_title: New title
            
        Returns:
            True if successful
        """
        return self.client.rename_notebook(notebook_id, new_title)
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            True if successful
        """
        return self.client.delete_notebook(notebook_id)
    
    def get_notebook_summary(self, notebook_id: str) -> dict:
        """Get AI-generated notebook summary.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            Summary dictionary with 'summary' and 'suggested_topics'
        """
        result = self.client.get_notebook_summary(notebook_id)
        return {
            "summary": result.get("summary", "") if result else "",
            "suggested_topics": result.get("suggested_topics", []) if result else [],
        }
    
    # =========================================================================
    # Query Operations
    # =========================================================================
    
    def query(
        self,
        notebook_id: str,
        query_text: str,
        source_ids: list[str] = None,
        conversation_id: str = None,
        timeout: float = None,
    ) -> dict:
        """Query a notebook with AI.
        
        Args:
            notebook_id: Notebook UUID
            query_text: Question to ask
            source_ids: Optional list of source IDs to query
            conversation_id: Optional conversation ID for follow-up
            timeout: Query timeout in seconds
            
        Returns:
            Query result with answer and metadata
        """
        result = self.client.query(
            notebook_id=notebook_id,
            query_text=query_text,
            source_ids=source_ids,
            conversation_id=conversation_id,
            timeout=timeout or self.settings.notebooklm_query_timeout,
        )
        return {
            "answer": result.get("answer", "") if result else "",
            "conversation_id": result.get("conversation_id") if result else None,
            "sources_used": result.get("sources_used", []) if result else [],
            "citations": result.get("citations", {}) if result else {},
        }
    
    # =========================================================================
    # Source Operations
    # =========================================================================
    
    def list_sources(self, notebook_id: str) -> list[dict]:
        """List sources in a notebook.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            List of source dictionaries
        """
        sources = self.client.get_notebook_sources_with_types(notebook_id)
        return sources if sources else []
    
    def add_url_source(self, notebook_id: str, url: str) -> dict:
        """Add a URL as a source.
        
        Args:
            notebook_id: Notebook UUID
            url: URL to add
            
        Returns:
            Source info dictionary
        """
        result = self.client.add_url_source(notebook_id, url)
        return result if result else {}
    
    def add_text_source(self, notebook_id: str, text: str, title: str = "") -> dict:
        """Add text as a source.
        
        Args:
            notebook_id: Notebook UUID
            text: Text content
            title: Optional title
            
        Returns:
            Source info dictionary
        """
        result = self.client.add_text_source(notebook_id, text, title=title)
        return result if result else {}
    
    def add_drive_source(self, notebook_id: str, drive_id: str, drive_type: str = "document") -> dict:
        """Add a Google Drive document as a source.
        
        Args:
            notebook_id: Notebook UUID
            drive_id: Google Drive file ID
            drive_type: Type of drive document
            
        Returns:
            Source info dictionary
        """
        result = self.client.add_drive_source(notebook_id, drive_id, drive_type=drive_type)
        return result if result else {}
    
    def delete_source(self, notebook_id: str, source_id: str) -> bool:
        """Delete a source from a notebook.
        
        Args:
            notebook_id: Notebook UUID
            source_id: Source UUID
            
        Returns:
            True if successful
        """
        return self.client.delete_source(notebook_id, source_id)
    
    def sync_drive_source(self, notebook_id: str, source_id: str) -> bool:
        """Sync a Drive source with latest content.
        
        Args:
            notebook_id: Notebook UUID
            source_id: Source UUID
            
        Returns:
            True if successful
        """
        return self.client.sync_drive_source(notebook_id, source_id)
    
    # =========================================================================
    # Studio Operations
    # =========================================================================
    
    def create_audio_overview(
        self,
        notebook_id: str,
        source_ids: list[str] = None,
        audio_format: str = "deep_dive",
        audio_length: str = "default",
        language: str = None,
        focus_prompt: str = "",
    ) -> dict:
        """Create an audio overview (podcast).
        
        Args:
            notebook_id: Notebook UUID
            source_ids: Optional list of source IDs
            audio_format: Format type (deep_dive, overview, etc.)
            audio_length: Length type
            language: Language code
            focus_prompt: Optional focus prompt
            
        Returns:
            Creation result with artifact_id
        """
        from notebooklm_tools.core import constants
        
        format_code = constants.AUDIO_FORMATS.get_code(audio_format)
        length_code = constants.AUDIO_LENGTHS.get_code(audio_length)
        
        result = self.client.create_audio_overview(
            notebook_id,
            source_ids=source_ids,
            format_code=format_code,
            length_code=length_code,
            language=language or self.settings.notebooklm_language,
            focus_prompt=focus_prompt,
        )
        return result if result else {}
    
    def create_video_overview(
        self,
        notebook_id: str,
        source_ids: list[str] = None,
        video_format: str = "explainer",
        visual_style: str = "auto_select",
        language: str = None,
        focus_prompt: str = "",
    ) -> dict:
        """Create a video overview.
        
        Args:
            notebook_id: Notebook UUID
            source_ids: Optional list of source IDs
            video_format: Format type
            visual_style: Visual style type
            language: Language code
            focus_prompt: Optional focus prompt
            
        Returns:
            Creation result with artifact_id
        """
        from notebooklm_tools.core import constants
        
        format_code = constants.VIDEO_FORMATS.get_code(video_format)
        style_code = constants.VIDEO_STYLES.get_code(visual_style)
        
        result = self.client.create_video_overview(
            notebook_id,
            source_ids=source_ids,
            format_code=format_code,
            visual_style_code=style_code,
            language=language or self.settings.notebooklm_language,
            focus_prompt=focus_prompt,
        )
        return result if result else {}
    
    def create_report(
        self,
        notebook_id: str,
        source_ids: list[str] = None,
        report_format: str = "Briefing Doc",
        custom_prompt: str = "",
        language: str = None,
    ) -> dict:
        """Create a report.
        
        Args:
            notebook_id: Notebook UUID
            source_ids: Optional list of source IDs
            report_format: Report format type
            custom_prompt: Optional custom prompt
            language: Language code
            
        Returns:
            Creation result with artifact_id
        """
        result = self.client.create_report(
            notebook_id,
            source_ids=source_ids,
            report_format=report_format,
            custom_prompt=custom_prompt,
            language=language or self.settings.notebooklm_language,
        )
        return result if result else {}
    
    def create_slide_deck(
        self,
        notebook_id: str,
        source_ids: list[str] = None,
        slide_format: str = "detailed_deck",
        slide_length: str = "default",
        language: str = None,
        focus_prompt: str = "",
    ) -> dict:
        """Create a slide deck.
        
        Args:
            notebook_id: Notebook UUID
            source_ids: Optional list of source IDs
            slide_format: Slide format type
            slide_length: Length type
            language: Language code
            focus_prompt: Optional focus prompt
            
        Returns:
            Creation result with artifact_id
        """
        from notebooklm_tools.core import constants
        
        format_code = constants.SLIDE_DECK_FORMATS.get_code(slide_format)
        length_code = constants.SLIDE_DECK_LENGTHS.get_code(slide_length)
        
        result = self.client.create_slide_deck(
            notebook_id,
            source_ids=source_ids,
            format_code=format_code,
            length_code=length_code,
            language=language or self.settings.notebooklm_language,
            focus_prompt=focus_prompt,
        )
        return result if result else {}
    
    def create_mind_map(
        self,
        notebook_id: str,
        source_ids: list[str] = None,
        title: str = "Mind Map",
    ) -> dict:
        """Create a mind map.
        
        Args:
            notebook_id: Notebook UUID
            source_ids: Optional list of source IDs
            title: Mind map title
            
        Returns:
            Creation result with artifact_id
        """
        # Generate mind map
        gen_result = self.client.generate_mind_map(
            notebook_id=notebook_id,
            source_ids=source_ids,
        )
        
        if not gen_result or not gen_result.get("mind_map_json"):
            raise Exception("Failed to generate mind map")
        
        # Save mind map
        result = self.client.save_mind_map(
            notebook_id,
            gen_result["mind_map_json"],
            source_ids=source_ids,
            title=title,
        )
        return result if result else {}
    
    def get_studio_status(self, notebook_id: str) -> list[dict]:
        """Get status of all studio artifacts.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            List of artifact status dictionaries
        """
        artifacts = self.client.poll_studio_status(notebook_id)
        
        # Also get mind maps
        try:
            mind_maps = self.client.list_mind_maps(notebook_id)
            for mm in mind_maps:
                artifacts.append({
                    "artifact_id": mm.get("mind_map_id"),
                    "type": "mind_map",
                    "title": mm.get("title", "Mind Map"),
                    "status": "completed",
                    "created_at": mm.get("created_at"),
                })
        except Exception:
            pass
        
        return artifacts
    
    # =========================================================================
    # Research Operations
    # =========================================================================
    
    def start_research(
        self,
        notebook_id: str,
        query: str,
        research_type: str = "fast",
        source_type: str = "web",
    ) -> dict:
        """Start a research operation.
        
        Args:
            notebook_id: Notebook UUID
            query: Research query
            research_type: 'fast' or 'deep'
            source_type: 'web' or 'drive'
            
        Returns:
            Research info with research_id
        """
        if research_type == "deep":
            result = self.client.start_deep_research(notebook_id, query)
        else:
            result = self.client.start_fast_research(notebook_id, query, source_type=source_type)
        return result if result else {}
    
    def poll_research(self, notebook_id: str, research_id: str) -> dict:
        """Poll research status.
        
        Args:
            notebook_id: Notebook UUID
            research_id: Research operation ID
            
        Returns:
            Research status and results
        """
        result = self.client.poll_research(notebook_id, research_id)
        return result if result else {}
    
    def import_research_sources(
        self,
        notebook_id: str,
        research_id: str,
        source_ids: list[str] = None,
    ) -> dict:
        """Import sources from research.
        
        Args:
            notebook_id: Notebook UUID
            research_id: Research operation ID
            source_ids: Optional list of specific source IDs to import
            
        Returns:
            Import result
        """
        result = self.client.import_research_sources(notebook_id, research_id, source_ids=source_ids)
        return result if result else {}
    
    # =========================================================================
    # Sharing Operations
    # =========================================================================
    
    def get_share_status(self, notebook_id: str) -> dict:
        """Get sharing status of a notebook.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            Share status dictionary
        """
        result = self.client.get_share_status(notebook_id)
        return result if result else {}
    
    def set_public_access(self, notebook_id: str, public: bool = True) -> bool:
        """Enable or disable public access.
        
        Args:
            notebook_id: Notebook UUID
            public: True to enable, False to disable
            
        Returns:
            True if successful
        """
        return self.client.set_public_access(notebook_id, public=public)
    
    def add_collaborator(self, notebook_id: str, email: str, role: str = "reader") -> bool:
        """Add a collaborator to a notebook.
        
        Args:
            notebook_id: Notebook UUID
            email: Collaborator email
            role: 'reader' or 'writer'
            
        Returns:
            True if successful
        """
        return self.client.add_collaborator(notebook_id, email, role=role)
    
    # =========================================================================
    # Notes Operations
    # =========================================================================
    
    def list_notes(self, notebook_id: str) -> list[dict]:
        """List notes in a notebook.
        
        Args:
            notebook_id: Notebook UUID
            
        Returns:
            List of note dictionaries
        """
        notes = self.client.list_notes(notebook_id)
        return notes if notes else []
    
    def create_note(self, notebook_id: str, title: str, content: str = "") -> dict:
        """Create a note in a notebook.
        
        Args:
            notebook_id: Notebook UUID
            title: Note title
            content: Note content
            
        Returns:
            Created note info
        """
        result = self.client.create_note(notebook_id, title, content=content)
        return result if result else {}
    
    def update_note(self, notebook_id: str, note_id: str, title: str = None, content: str = None) -> bool:
        """Update a note.
        
        Args:
            notebook_id: Notebook UUID
            note_id: Note UUID
            title: Optional new title
            content: Optional new content
            
        Returns:
            True if successful
        """
        return self.client.update_note(notebook_id, note_id, title=title, content=content)
    
    def delete_note(self, notebook_id: str, note_id: str) -> bool:
        """Delete a note.
        
        Args:
            notebook_id: Notebook UUID
            note_id: Note UUID
            
        Returns:
            True if successful
        """
        return self.client.delete_note(notebook_id, note_id)


# Global client instance
_client_instance: Optional[NotebookLMClientWrapper] = None


def get_client() -> NotebookLMClientWrapper:
    """Get the global client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = NotebookLMClientWrapper()
    return _client_instance


@contextmanager
def client_context():
    """Context manager for client usage."""
    client = get_client()
    try:
        yield client
    finally:
        pass  # Client is reused, don't close
