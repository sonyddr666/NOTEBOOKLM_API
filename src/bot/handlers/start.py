"""Start and help handlers."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src import __version__
from src.bot.keyboards import main_menu_keyboard
from src.bot.middleware import rate_limit_middleware


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    user = update.effective_user
    
    welcome_text = f"""
👋 Welcome to *NotebookLM Bot*, {user.first_name}!

I help you interact with Google NotebookLM through Telegram.

📚 *What I can do:*
• Manage your notebooks
• Add sources (URLs, text, files)
• Query notebooks with AI
• Generate audio podcasts
• Create reports and slides
• Share notebooks

🚀 *Quick Start:*
1. Use /notebooks to see your notebooks
2. Use /create to make a new notebook
3. Use /query to chat with a notebook

💡 *Tip:* Use the buttons below to navigate!
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    help_text = """
📖 *NotebookLM Bot Help*

*Basic Commands:*
/start - Start the bot
/help - Show this help message
/notebooks - List all notebooks
/create <title> - Create a new notebook

*Notebook Commands:*
/notebook <id> - View notebook details
/rename <id> <title> - Rename notebook
/delete <id> - Delete notebook

*Source Commands:*
/sources <notebook_id> - List sources
/add_url <notebook_id> <url> - Add URL source
/add_text <notebook_id> <text> - Add text source

*Query Commands:*
/query <notebook_id> <question> - Ask a question
/chat <notebook_id> - Start interactive chat

*Studio Commands:*
/audio <notebook_id> - Generate audio overview
/video <notebook_id> - Generate video overview
/report <notebook_id> - Generate report
/status <notebook_id> - Check studio status

*Sharing Commands:*
/share <notebook_id> - View sharing options
/public <notebook_id> - Make notebook public
/private <notebook_id> - Make notebook private

*Admin Commands:*
/auth - Check authentication status

💡 *Tips:*
• Use inline buttons for easy navigation
• Send any message while in chat mode to continue conversation
• Use /cancel to exit chat mode

⚠️ *Note:* You need to authenticate first using 'nlm login' on the server.
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )


async def auth_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /auth command to check authentication status."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    try:
        from src.core import get_client
        
        client = get_client()
        # Try to list notebooks to verify auth
        notebooks = client.list_notebooks(max_results=1)
        
        await update.message.reply_text(
            "✅ *Authentication Status: Valid*\n\n"
            f"Successfully connected to NotebookLM.\n"
            f"Found {len(notebooks)} notebook(s).",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Authentication Status: Failed*\n\n"
            f"Error: {str(e)}\n\n"
            f"Please run 'nlm login' on the server to authenticate.",
            parse_mode="Markdown",
        )


# Handler instances
start_handler = CommandHandler("start", start)
help_handler = CommandHandler("help", help_command)
auth_handler = CommandHandler("auth", auth_status)
