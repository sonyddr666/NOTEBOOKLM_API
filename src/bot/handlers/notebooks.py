"""Notebook command handlers."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.core import get_client, NotebookLMError
from src.bot.keyboards import notebooks_list_keyboard, notebook_actions_keyboard
from src.bot.middleware import rate_limit_middleware


async def notebooks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /notebooks command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    try:
        client = get_client()
        notebooks_list = client.list_notebooks()
        
        if not notebooks_list:
            await update.message.reply_text(
                "📭 No notebooks found.\n\n"
                "Use /create <title> to create a new notebook.",
            )
            return
        
        # Store notebooks in context for later use
        context.user_data["notebooks"] = notebooks_list
        
        text = f"📚 *Your Notebooks* ({len(notebooks_list)} total)\n\n"
        text += "Select a notebook to view details:"
        
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=notebooks_list_keyboard(notebooks_list),
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to list notebooks: {str(e)}")


async def create_notebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /create command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    # Get title from arguments
    title = " ".join(context.args) if context.args else ""
    
    try:
        client = get_client()
        result = client.create_notebook(title=title)
        
        await update.message.reply_text(
            f"✅ *Notebook Created!*\n\n"
            f"📝 Title: {result['title']}\n"
            f"🆔 ID: `{result['id']}`\n"
            f"🔗 URL: {result['url']}",
            parse_mode="Markdown",
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to create notebook: {str(e)}")


async def notebook_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /notebook <id> command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /notebook <notebook_id>\n\n"
            "Use /notebooks to list all notebooks."
        )
        return
    
    notebook_id = context.args[0]
    
    try:
        client = get_client()
        nb = client.get_notebook(notebook_id)
        sources = client.list_sources(notebook_id)
        
        text = f"📖 *{nb['title']}*\n\n"
        text += f"🆔 ID: `{nb['id']}`\n"
        text += f"📄 Sources: {len(sources)}\n"
        text += f"🔗 [Open in NotebookLM]({nb['url']})\n"
        
        if sources:
            text += "\n*Sources:*\n"
            for src in sources[:5]:
                text += f"• {src.get('title', 'Untitled')}\n"
            if len(sources) > 5:
                text += f"... and {len(sources) - 5} more\n"
        
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=notebook_actions_keyboard(notebook_id),
            disable_web_page_preview=True,
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to get notebook: {str(e)}")


async def rename_notebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /rename command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /rename <notebook_id> <new_title>"
        )
        return
    
    notebook_id = context.args[0]
    new_title = " ".join(context.args[1:])
    
    try:
        client = get_client()
        client.rename_notebook(notebook_id, new_title)
        
        await update.message.reply_text(
            f"✅ Notebook renamed to: *{new_title}*",
            parse_mode="Markdown",
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to rename notebook: {str(e)}")


async def delete_notebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /delete command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /delete <notebook_id>\n\n"
            "⚠️ This action cannot be undone!"
        )
        return
    
    notebook_id = context.args[0]
    
    try:
        client = get_client()
        
        # Get notebook info first
        nb = client.get_notebook(notebook_id)
        
        # Store in context for confirmation
        context.user_data["delete_notebook_id"] = notebook_id
        context.user_data["delete_notebook_title"] = nb["title"]
        
        from src.bot.keyboards import confirm_delete_keyboard
        
        await update.message.reply_text(
            f"⚠️ *Confirm Deletion*\n\n"
            f"Are you sure you want to delete:\n"
            f"📖 *{nb['title']}*\n\n"
            f"This action cannot be undone!",
            parse_mode="Markdown",
            reply_markup=confirm_delete_keyboard(notebook_id),
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to delete notebook: {str(e)}")


# Handler instances
notebooks_handler = CommandHandler("notebooks", notebooks)
create_notebook_handler = CommandHandler("create", create_notebook)
notebook_info_handler = CommandHandler("notebook", notebook_info)
rename_handler = CommandHandler("rename", rename_notebook)
delete_handler = CommandHandler("delete", delete_notebook)
