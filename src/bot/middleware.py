"""Middleware for Telegram bot."""

import time
from collections import defaultdict
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from src.config import get_settings

settings = get_settings()

# Rate limiting storage
user_last_message: dict[int, float] = defaultdict(float)
user_message_count: dict[int, list[float]] = defaultdict(list)


def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """Check if user is within rate limits.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Tuple of (is_allowed, retry_after_seconds)
    """
    now = time.time()
    minute_ago = now - 60
    
    # Clean old messages
    user_message_count[user_id] = [
        t for t in user_message_count[user_id] if t > minute_ago
    ]
    
    # Check rate limit
    if len(user_message_count[user_id]) >= settings.telegram_rate_limit:
        oldest = min(user_message_count[user_id])
        retry_after = int(60 - (now - oldest)) + 1
        return False, retry_after
    
    # Record this message
    user_message_count[user_id].append(now)
    return True, 0


def is_user_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is allowed
    """
    # If no allowlist, everyone is allowed
    if not settings.telegram_allowed_users:
        return True
    
    # Check if user is in allowlist or is admin
    return (
        user_id in settings.telegram_allowed_users or
        user_id in settings.telegram_admin_users
    )


def is_admin(user_id: int) -> bool:
    """Check if user is an admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is an admin
    """
    return user_id in settings.telegram_admin_users


async def rate_limit_middleware(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Rate limiting middleware.
    
    Returns:
        True if request should proceed, False if rate limited
    """
    if not update.effective_user:
        return True
    
    user_id = update.effective_user.id
    
    # Check if user is allowed
    if not is_user_allowed(user_id):
        if update.message:
            await update.message.reply_text(
                "⛔ You are not authorized to use this bot."
            )
        return False
    
    # Check rate limit
    allowed, retry_after = check_rate_limit(user_id)
    if not allowed:
        if update.message:
            await update.message.reply_text(
                f"⏳ Rate limit exceeded. Please try again in {retry_after} seconds."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                f"Rate limited. Try again in {retry_after}s",
                show_alert=True
            )
        return False
    
    return True


# User state management for multi-step conversations
user_states: dict[int, dict] = defaultdict(dict)


def set_user_state(user_id: int, state: str, data: dict = None) -> None:
    """Set user state for multi-step conversations.
    
    Args:
        user_id: Telegram user ID
        state: State name
        data: Optional state data
    """
    user_states[user_id] = {
        "state": state,
        "data": data or {},
        "timestamp": time.time(),
    }


def get_user_state(user_id: int) -> dict | None:
    """Get user state.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        State dict or None
    """
    state = user_states.get(user_id)
    if state:
        # Expire states after 5 minutes
        if time.time() - state["timestamp"] > 300:
            clear_user_state(user_id)
            return None
    return state


def clear_user_state(user_id: int) -> None:
    """Clear user state.
    
    Args:
        user_id: Telegram user ID
    """
    if user_id in user_states:
        del user_states[user_id]


# Conversation states for ConversationHandler
(
    STATE_MAIN_MENU,
    STATE_NOTEBOOK_LIST,
    STATE_NOTEBOOK_VIEW,
    STATE_QUERY,
    STATE_ADD_SOURCE,
    STATE_CREATE_NOTEBOOK,
    STATE_SHARE,
) = range(7)
