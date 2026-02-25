"""Main Telegram bot application."""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from src.config import get_settings
from src.bot.handlers.start import start_handler, help_handler, auth_handler
from src.bot.handlers.auth import cookies_handler, cookie_message_handler
from src.bot.handlers.notebooks import (
    notebooks_handler,
    create_notebook_handler,
    notebook_info_handler,
    rename_handler,
    delete_handler,
)
from src.bot.handlers.chat import (
    query_handler,
    chat_handler,
    cancel_handler,
    message_handler,
)
from src.bot.handlers.callbacks import callback_handler
from src.bot.middleware import get_user_state, clear_user_state, set_user_state

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

settings = get_settings()


def check_bot_token():
    """Check if bot token is configured."""
    if not settings.telegram_bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not configured. "
            "Set it in .env file or environment variable."
        )


async def handle_text_message(update: Update, context) -> None:
    """Handle text messages for multi-step conversations."""
    if not update.effective_user or not update.message:
        return
    
    # Check if we are waiting for cookies from the other handler
    if context.user_data.get("awaiting_cookies"):
        return
    
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    if not state:
        # No active state, ignore message
        return
    
    state_name = state["state"]
    state_data = state["data"]
    
    try:
        if state_name == "create_notebook":
            # Create notebook with the message as title
            from src.core import get_client
            client = get_client()
            title = update.message.text
            result = client.create_notebook(title=title)
            
            clear_user_state(user_id)
            await update.message.reply_text(
                f"✅ *Notebook Created!*\n\n"
                f"📝 Title: {result['title']}\n"
                f"🆔 ID: `{result['id']}`",
                parse_mode="Markdown",
            )
        
        elif state_name == "add_url":
            # Add URL source
            from src.core import get_client
            client = get_client()
            notebook_id = state_data.get("notebook_id")
            url = update.message.text
            
            result = client.add_url_source(notebook_id, url)
            clear_user_state(user_id)
            
            await update.message.reply_text(
                f"✅ URL added as source!\n\n"
                f"🔗 URL: {url}",
            )
        
        elif state_name == "add_text":
            # Add text source
            from src.core import get_client
            client = get_client()
            notebook_id = state_data.get("notebook_id")
            text = update.message.text
            
            result = client.add_text_source(notebook_id, text)
            clear_user_state(user_id)
            
            await update.message.reply_text(
                f"✅ Text added as source!",
            )
        
        elif state_name == "chat":
            # Handle chat message
            from src.bot.handlers.chat import _execute_query
            notebook_id = state_data.get("notebook_id")
            conversation_id = state_data.get("conversation_id")
            
            await _execute_query(
                update, context, 
                notebook_id, 
                update.message.text,
                conversation_id
            )
    
    except Exception as e:
        clear_user_state(user_id)
        await update.message.reply_text(f"❌ Error: {str(e)}")


def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    check_bot_token()
    
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    # Basic commands
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(auth_handler)
    application.add_handler(cookies_handler)
    application.add_handler(cookie_message_handler)
    
    # Notebook commands
    application.add_handler(notebooks_handler)
    application.add_handler(create_notebook_handler)
    application.add_handler(notebook_info_handler)
    application.add_handler(rename_handler)
    application.add_handler(delete_handler)
    
    # Query/Chat commands
    application.add_handler(query_handler)
    application.add_handler(chat_handler)
    application.add_handler(cancel_handler)
    
    # Callback handler (for inline keyboards)
    application.add_handler(callback_handler)
    
    # Text message handler (for multi-step conversations)
    # This should be added last to not interfere with other handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    return application


def run_bot():
    """Run the Telegram bot."""
    logger.info("Starting NotebookLM Telegram Bot...")
    
    application = create_application()
    
    # Run the bot
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    run_bot()
