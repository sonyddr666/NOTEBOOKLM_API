"""Authentication and cookie handlers."""

import json
import os
from pathlib import Path
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from src.config import get_settings
from src.bot.middleware import rate_limit_middleware

settings = get_settings()

async def cookies_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cookies command to start cookie import process."""
    # Check if user is admin
    user_id = update.effective_user.id
    if user_id not in settings.telegram_admin_users:
        await update.message.reply_text("❌ *Unauthorized:* You don't have permission to use this command.")
        return

    await update.message.reply_text(
        "📝 *Cookie Import*\n\n"
        "Please send the *JSON content* of your cookies or upload a *cookies.json* file.\n\n"
        "💡 *Tip:* You can export these using 'EditThisCookie' extension in format JSON.",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_cookies"] = True

async def handle_cookie_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the actual cookie data (text or file)."""
    if not context.user_data.get("awaiting_cookies"):
        return

    # Check if user is admin again for safety
    user_id = update.effective_user.id
    if user_id not in settings.telegram_admin_users:
        return

    cookie_data = ""
    
    # Handle file upload
    if update.message.document:
        try:
            doc = update.message.document
            await update.message.reply_text(f"📥 Processing file: `{doc.file_name}`...", parse_mode="Markdown")
            
            file = await context.bot.get_file(doc.file_id)
            content = await file.download_as_bytearray()
            cookie_data = content.decode('utf-8')
        except Exception as e:
            await update.message.reply_text(f"❌ Error downloading file: {str(e)}")
            return
    # Handle text message
    elif update.message.text:
        cookie_data = update.message.text

    if not cookie_data:
        return

    try:
        # Validate JSON
        cookies = json.loads(cookie_data)
        if not isinstance(cookies, list):
            await update.message.reply_text("❌ *Error:* Cookies must be a list of objects.")
            return

        # Ensure directory exists
        settings.notebooklm_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to the correct location
        cookie_file = settings.cookies_file
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        # Also create a dummy auth.json if it doesn't exist to satisfy the client
        auth_file = settings.auth_file
        if not auth_file.exists():
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump({"email": "authenticated@via-telegram.com", "profile": settings.notebooklm_profile}, f)

        await update.message.reply_text(
            f"✅ *Cookies saved successfully!*\n\n"
            f"Location: `{cookie_file}`\n\n"
            f"Now try /auth to verify the connection.",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_cookies"] = False
        
    except json.JSONDecodeError:
        await update.message.reply_text("❌ *Error:* Invalid JSON format. Please check the content and try again.")
    except Exception as e:
        await update.message.reply_text(f"❌ *Error saving cookies:* {str(e)}")

# Handler instances
cookies_handler = CommandHandler("cookies", cookies_command)
cookie_message_handler = MessageHandler(
    (filters.TEXT | filters.Document.ALL) & ~filters.COMMAND, 
    handle_cookie_input
)
