"""Callback query handlers for inline keyboards."""

import asyncio
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.core import get_client, NotebookLMError
from src.bot.keyboards import (
    main_menu_keyboard,
    notebooks_list_keyboard,
    notebook_actions_keyboard,
    studio_menu_keyboard,
    sources_list_keyboard,
    share_keyboard,
    back_keyboard,
)
from src.bot.middleware import rate_limit_middleware, set_user_state, clear_user_state


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries."""
    query = update.callback_query
    
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    await query.answer()
    
    data = query.data
    
    try:
        # Main menu navigation
        if data == "menu_main":
            await show_main_menu(query)
        elif data == "menu_notebooks":
            await show_notebooks(query)
        elif data == "menu_create":
            await prompt_create(query, context)
        elif data == "menu_query":
            await prompt_query(query)
        elif data == "menu_studio":
            await prompt_studio(query)
        elif data == "menu_settings":
            await show_settings(query)
        elif data == "menu_help":
            await show_help(query)
        
        # Notebook selection
        elif data.startswith("notebook_"):
            notebook_id = data[9:]
            await show_notebook(query, notebook_id)
        
        # Notebook actions
        elif data.startswith("query_"):
            notebook_id = data[6:]
            await start_query_mode(query, context, notebook_id)
        elif data.startswith("sources_"):
            notebook_id = data[8:]
            await show_sources(query, notebook_id)
        elif data.startswith("audio_"):
            notebook_id = data[6:]
            await create_audio(query, notebook_id)
        elif data.startswith("video_"):
            notebook_id = data[6:]
            await create_video(query, notebook_id)
        elif data.startswith("status_"):
            notebook_id = data[7:]
            await show_status(query, notebook_id)
        elif data.startswith("share_"):
            notebook_id = data[6:]
            await show_share(query, notebook_id)
        elif data.startswith("notes_"):
            notebook_id = data[6:]
            await show_notes(query, notebook_id)
        elif data.startswith("delete_"):
            notebook_id = data[7:]
            await confirm_delete(query, notebook_id)
        elif data.startswith("confirm_delete_"):
            notebook_id = data[15:]
            await do_delete(query, notebook_id)
        
        # Studio creation
        elif data.startswith("create_audio_"):
            notebook_id = data[13:]
            await create_audio(query, notebook_id)
        elif data.startswith("create_video_"):
            notebook_id = data[13:]
            await create_video(query, notebook_id)
        elif data.startswith("create_report_"):
            notebook_id = data[14:]
            await create_report(query, notebook_id)
        elif data.startswith("create_slides_"):
            notebook_id = data[14:]
            await create_slides(query, notebook_id)
        elif data.startswith("create_mindmap_"):
            notebook_id = data[15:]
            await create_mindmap(query, notebook_id)
        elif data.startswith("create_flashcards_"):
            notebook_id = data[18:]
            await create_flashcards(query, notebook_id)
        
        # Source actions
        elif data.startswith("add_url_"):
            notebook_id = data[8:]
            await prompt_add_url(query, context, notebook_id)
        elif data.startswith("add_text_"):
            notebook_id = data[9:]
            await prompt_add_text(query, context, notebook_id)
        
        # Share actions
        elif data.startswith("make_public_"):
            notebook_id = data[12:]
            await make_public(query, notebook_id)
        elif data.startswith("make_private_"):
            notebook_id = data[13:]
            await make_private(query, notebook_id)
        
        # Cancel
        elif data == "cancel":
            clear_user_state(query.from_user.id)
            await query.edit_message_text(
                "✅ Action cancelled.",
                reply_markup=main_menu_keyboard(),
            )
        
        else:
            await query.edit_message_text(
                "❓ Unknown action. Use the menu below.",
                reply_markup=main_menu_keyboard(),
            )
            
    except NotebookLMError as e:
        await query.edit_message_text(
            f"❌ Error: {e.message}",
            reply_markup=back_keyboard("menu_main"),
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Failed: {str(e)}",
            reply_markup=back_keyboard("menu_main"),
        )


# ============================================================================
# Menu Handlers
# ============================================================================

async def show_main_menu(query) -> None:
    """Show main menu."""
    await query.edit_message_text(
        "🏠 *Main Menu*\n\nSelect an option:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def show_notebooks(query) -> None:
    """Show notebooks list."""
    client = get_client()
    notebooks = client.list_notebooks()
    
    if not notebooks:
        await query.edit_message_text(
            "📭 No notebooks found.\n\n"
            "Use the Create button to make a new notebook.",
            reply_markup=back_keyboard(),
        )
        return
    
    text = f"📚 *Your Notebooks* ({len(notebooks)} total)\n\n"
    text += "Select a notebook:"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=notebooks_list_keyboard(notebooks),
    )


async def prompt_create(query, context) -> None:
    """Prompt for notebook creation."""
    set_user_state(query.from_user.id, "create_notebook", {})
    await query.edit_message_text(
        "📝 *Create New Notebook*\n\n"
        "Send me the title for your new notebook:\n\n"
        "Example: My Research Notes",
        parse_mode="Markdown",
        reply_markup=back_keyboard(),
    )


async def prompt_query(query) -> None:
    """Prompt for query."""
    await query.edit_message_text(
        "🔍 *Query a Notebook*\n\n"
        "Usage: /query <notebook_id> <question>\n\n"
        "Or use /chat <notebook_id> for interactive mode.",
        parse_mode="Markdown",
        reply_markup=back_keyboard(),
    )


async def prompt_studio(query) -> None:
    """Prompt for studio selection."""
    client = get_client()
    notebooks = client.list_notebooks()
    
    if not notebooks:
        await query.edit_message_text(
            "📭 No notebooks found.\n\n"
            "Create a notebook first to generate content.",
            reply_markup=back_keyboard(),
        )
        return
    
    await query.edit_message_text(
        "🎙️ *Studio Content*\n\n"
        "Select a notebook first, then choose what to create.",
        parse_mode="Markdown",
        reply_markup=notebooks_list_keyboard(notebooks),
    )


async def show_settings(query) -> None:
    """Show settings."""
    await query.edit_message_text(
        "⚙️ *Settings*\n\n"
        "No configurable settings yet.\n\n"
        "Use /auth to check authentication status.",
        parse_mode="Markdown",
        reply_markup=back_keyboard(),
    )


async def show_help(query) -> None:
    """Show help."""
    text = """
📖 *Help*

*Quick Commands:*
/notebooks - List notebooks
/create <title> - Create notebook
/query <id> <question> - Ask question
/chat <id> - Interactive chat

*Studio Commands:*
/audio <id> - Generate audio
/status <id> - Check status

*More Help:*
Use /help for full command list.
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_keyboard(),
    )


# ============================================================================
# Notebook Handlers
# ============================================================================

async def show_notebook(query, notebook_id: str) -> None:
    """Show notebook details."""
    client = get_client()
    nb = client.get_notebook(notebook_id)
    sources = client.list_sources(notebook_id)
    
    text = f"📖 *{nb['title']}*\n\n"
    text += f"🆔 ID: `{nb['id']}`\n"
    text += f"📄 Sources: {len(sources)}\n"
    
    if sources:
        text += "\n*Recent Sources:*\n"
        for src in sources[:3]:
            text += f"• {src.get('title', 'Untitled')}\n"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=notebook_actions_keyboard(notebook_id),
    )


async def show_sources(query, notebook_id: str) -> None:
    """Show sources in a notebook."""
    client = get_client()
    sources = client.list_sources(notebook_id)
    
    if not sources:
        await query.edit_message_text(
            "📄 No sources in this notebook.\n\n"
            "Use the buttons below to add sources.",
            reply_markup=sources_list_keyboard(notebook_id, []),
        )
        return
    
    text = f"📄 *Sources* ({len(sources)} total)\n\n"
    for src in sources[:10]:
        text += f"• {src.get('title', 'Untitled')}\n"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=sources_list_keyboard(notebook_id, sources),
    )


async def show_status(query, notebook_id: str) -> None:
    """Show studio status."""
    client = get_client()
    artifacts = client.get_studio_status(notebook_id)
    
    if not artifacts:
        await query.edit_message_text(
            "📊 No studio content found.\n\n"
            "Use the Studio menu to create content.",
            reply_markup=back_keyboard(f"notebook_{notebook_id}"),
        )
        return
    
    text = "📊 *Studio Status*\n\n"
    for artifact in artifacts[:10]:
        status_emoji = "✅" if artifact.get("status") == "completed" else "⏳"
        text += f"{status_emoji} {artifact.get('type', 'Unknown')}: {artifact.get('title', 'Untitled')}\n"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )


async def show_share(query, notebook_id: str) -> None:
    """Show sharing options."""
    client = get_client()
    status = client.get_share_status(notebook_id)
    
    is_public = status.get("is_public", False)
    public_url = status.get("public_url", "")
    
    text = "🔗 *Sharing Options*\n\n"
    if is_public:
        text += f"🌍 Status: Public\n"
        text += f"🔗 URL: `{public_url}`\n"
    else:
        text += f"🔒 Status: Private\n"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=share_keyboard(notebook_id, is_public),
    )


async def show_notes(query, notebook_id: str) -> None:
    """Show notes in a notebook."""
    client = get_client()
    notes = client.list_notes(notebook_id)
    
    if not notes:
        await query.edit_message_text(
            "📝 No notes in this notebook.",
            reply_markup=back_keyboard(f"notebook_{notebook_id}"),
        )
        return
    
    text = f"📝 *Notes* ({len(notes)} total)\n\n"
    for note in notes[:10]:
        text += f"• {note.get('title', 'Untitled')}\n"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )


async def confirm_delete(query, notebook_id: str) -> None:
    """Confirm notebook deletion."""
    from src.bot.keyboards import confirm_delete_keyboard
    
    client = get_client()
    nb = client.get_notebook(notebook_id)
    
    await query.edit_message_text(
        f"⚠️ *Confirm Deletion*\n\n"
        f"Delete: *{nb['title']}*\n\n"
        f"This cannot be undone!",
        parse_mode="Markdown",
        reply_markup=confirm_delete_keyboard(notebook_id),
    )


async def do_delete(query, notebook_id: str) -> None:
    """Execute notebook deletion."""
    client = get_client()
    client.delete_notebook(notebook_id)
    
    await query.edit_message_text(
        "✅ Notebook deleted successfully.",
        reply_markup=back_keyboard("menu_notebooks"),
    )


# ============================================================================
# Studio Handlers
# ============================================================================

async def create_audio(query, notebook_id: str) -> None:
    """Create audio overview."""
    client = get_client()
    
    await query.edit_message_text(
        "🎙️ Starting audio generation...\n"
        "This may take a few minutes.",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    result = client.create_audio_overview(notebook_id)
    
    await query.message.reply_text(
        f"✅ Audio generation started!\n\n"
        f"Artifact ID: `{result.get('artifact_id', 'N/A')}`\n\n"
        f"Use /status {notebook_id} to check progress.",
        parse_mode="Markdown",
    )


async def create_video(query, notebook_id: str) -> None:
    """Create video overview."""
    client = get_client()
    
    await query.edit_message_text(
        "🎬 Starting video generation...\n"
        "This may take several minutes.",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    result = client.create_video_overview(notebook_id)
    
    await query.message.reply_text(
        f"✅ Video generation started!\n\n"
        f"Artifact ID: `{result.get('artifact_id', 'N/A')}`\n\n"
        f"Use /status {notebook_id} to check progress.",
        parse_mode="Markdown",
    )


async def create_report(query, notebook_id: str) -> None:
    """Create report."""
    client = get_client()
    
    await query.edit_message_text(
        "📊 Starting report generation...",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    result = client.create_report(notebook_id)
    
    await query.message.reply_text(
        f"✅ Report generation started!\n\n"
        f"Artifact ID: `{result.get('artifact_id', 'N/A')}`",
        parse_mode="Markdown",
    )


async def create_slides(query, notebook_id: str) -> None:
    """Create slide deck."""
    client = get_client()
    
    await query.edit_message_text(
        "📑 Starting slide deck generation...",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    result = client.create_slide_deck(notebook_id)
    
    await query.message.reply_text(
        f"✅ Slide deck generation started!\n\n"
        f"Artifact ID: `{result.get('artifact_id', 'N/A')}`",
        parse_mode="Markdown",
    )


async def create_mindmap(query, notebook_id: str) -> None:
    """Create mind map."""
    client = get_client()
    
    await query.edit_message_text(
        "🗺️ Creating mind map...",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    result = client.create_mind_map(notebook_id)
    
    await query.message.reply_text(
        f"✅ Mind map created!\n\n"
        f"ID: `{result.get('mind_map_id', 'N/A')}`",
        parse_mode="Markdown",
    )


async def create_flashcards(query, notebook_id: str) -> None:
    """Create flashcards."""
    client = get_client()
    
    await query.edit_message_text(
        "🎴 Starting flashcard generation...",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )
    
    # Use client directly for flashcards
    result = client.client.create_flashcards(notebook_id, source_ids=None)
    
    await query.message.reply_text(
        f"✅ Flashcards created!\n\n"
        f"Artifact ID: `{result.get('artifact_id', 'N/A')}`",
        parse_mode="Markdown",
    )


# ============================================================================
# Source Handlers
# ============================================================================

async def prompt_add_url(query, context, notebook_id: str) -> None:
    """Prompt for URL to add."""
    set_user_state(query.from_user.id, "add_url", {"notebook_id": notebook_id})
    
    await query.edit_message_text(
        "🔗 *Add URL Source*\n\n"
        "Send me the URL to add:\n\n"
        "Example: https://example.com/article",
        parse_mode="Markdown",
        reply_markup=back_keyboard(f"sources_{notebook_id}"),
    )


async def prompt_add_text(query, context, notebook_id: str) -> None:
    """Prompt for text to add."""
    set_user_state(query.from_user.id, "add_text", {"notebook_id": notebook_id})
    
    await query.edit_message_text(
        "📝 *Add Text Source*\n\n"
        "Send me the text to add as a source.",
        parse_mode="Markdown",
        reply_markup=back_keyboard(f"sources_{notebook_id}"),
    )


# ============================================================================
# Share Handlers
# ============================================================================

async def make_public(query, notebook_id: str) -> None:
    """Make notebook public."""
    client = get_client()
    client.set_public_access(notebook_id, public=True)
    status = client.get_share_status(notebook_id)
    
    await query.edit_message_text(
        f"🌍 Notebook is now public!\n\n"
        f"🔗 URL: `{status.get('public_url', 'N/A')}`",
        parse_mode="Markdown",
        reply_markup=share_keyboard(notebook_id, True),
    )


async def make_private(query, notebook_id: str) -> None:
    """Make notebook private."""
    client = get_client()
    client.set_public_access(notebook_id, public=False)
    
    await query.edit_message_text(
        "🔒 Notebook is now private.",
        reply_markup=share_keyboard(notebook_id, False),
    )


# ============================================================================
# Query Mode
# ============================================================================

async def start_query_mode(query, context, notebook_id: str) -> None:
    """Start query mode for a notebook."""
    set_user_state(query.from_user.id, "chat", {
        "notebook_id": notebook_id,
        "conversation_id": None,
    })
    
    await query.edit_message_text(
        "💬 *Query Mode*\n\n"
        "Send me your question about this notebook.\n"
        "Use /cancel to exit.",
        parse_mode="Markdown",
        reply_markup=back_keyboard(f"notebook_{notebook_id}"),
    )


# Handler instance
callback_handler = CallbackQueryHandler(handle_callback)
