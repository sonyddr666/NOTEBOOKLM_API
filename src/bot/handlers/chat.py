"""Chat and query handlers."""

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

from src.core import get_client, NotebookLMError
from src.bot.middleware import rate_limit_middleware, set_user_state, get_user_state, clear_user_state
from src.bot.keyboards import back_keyboard, cancel_keyboard


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /query command."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /query <notebook_id> <question>\n\n"
            "Example: /query abc123 What are the main topics?"
        )
        return
    
    notebook_id = context.args[0]
    question = " ".join(context.args[1:])
    
    await _execute_query(update, context, notebook_id, question)


async def _execute_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    notebook_id: str,
    question: str,
    conversation_id: str = None,
) -> None:
    """Execute a query and send the response."""
    try:
        client = get_client()
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        result = client.query(
            notebook_id=notebook_id,
            query_text=question,
            conversation_id=conversation_id,
        )
        
        answer = result.get("answer", "No answer received.")
        new_conversation_id = result.get("conversation_id")
        
        # Store conversation state for follow-up
        if new_conversation_id:
            set_user_state(
                update.effective_user.id,
                "chat",
                {
                    "notebook_id": notebook_id,
                    "conversation_id": new_conversation_id,
                }
            )
        
        # Truncate long answers
        if len(answer) > 4000:
            answer = answer[:3997] + "..."
        
        await update.message.reply_text(
            f"💬 *Answer:*\n\n{answer}",
            parse_mode="Markdown",
        )
        
        if new_conversation_id:
            await update.message.reply_text(
                "💬 Continue the conversation by sending more messages, "
                "or use /cancel to exit chat mode.",
                reply_markup=cancel_keyboard(),
            )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Query failed: {str(e)}")


async def chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chat command to start interactive chat mode."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /chat <notebook_id>\n\n"
            "Starts an interactive chat session with a notebook."
        )
        return
    
    notebook_id = context.args[0]
    
    try:
        client = get_client()
        nb = client.get_notebook(notebook_id)
        
        # Set chat mode state
        set_user_state(
            update.effective_user.id,
            "chat",
            {
                "notebook_id": notebook_id,
                "conversation_id": None,
            }
        )
        
        await update.message.reply_text(
            f"💬 *Chat Mode Started*\n\n"
            f"Notebook: *{nb['title']}*\n\n"
            f"Send any message to ask a question.\n"
            f"Use /cancel to exit chat mode.",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        
    except NotebookLMError as e:
        await update.message.reply_text(f"❌ Error: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to start chat: {str(e)}")


async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages in chat mode."""
    # Check rate limit
    if not await rate_limit_middleware(update, context):
        return
    
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    if not state or state["state"] != "chat":
        # Not in chat mode, ignore
        return
    
    # Get state data
    notebook_id = state["data"].get("notebook_id")
    conversation_id = state["data"].get("conversation_id")
    question = update.message.text
    
    if not notebook_id:
        clear_user_state(user_id)
        await update.message.reply_text(
            "❌ Chat session expired. Use /chat to start a new session."
        )
        return
    
    await _execute_query(update, context, notebook_id, question, conversation_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command to exit chat mode."""
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    if state:
        clear_user_state(user_id)
        await update.message.reply_text(
            "✅ Chat mode ended.",
        )
    else:
        await update.message.reply_text(
            "No active chat session to cancel.",
        )


# Handler instances
query_handler = CommandHandler("query", query)
chat_handler = CommandHandler("chat", chat_mode)
cancel_handler = CommandHandler("cancel", cancel)
message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_message)
