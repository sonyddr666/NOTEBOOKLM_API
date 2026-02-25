"""Inline keyboards for Telegram bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📚 Notebooks", callback_data="menu_notebooks"),
            InlineKeyboardButton("➕ Create", callback_data="menu_create"),
        ],
        [
            InlineKeyboardButton("🔍 Query", callback_data="menu_query"),
            InlineKeyboardButton("🎙️ Studio", callback_data="menu_studio"),
        ],
        [
            InlineKeyboardButton("🔬 Deep Research", callback_data="menu_research"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def notebooks_list_keyboard(notebooks: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard for selecting a notebook from a list."""
    keyboard = []
    for nb in notebooks[:10]:  # Limit to 10 buttons
        keyboard.append([
            InlineKeyboardButton(
                f"📖 {nb['title'][:30]}{'...' if len(nb['title']) > 30 else ''}",
                callback_data=f"notebook_{nb['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton("🔄 Refresh", callback_data="menu_notebooks"),
        InlineKeyboardButton("🏠 Main", callback_data="menu_main"),
    ])
    return InlineKeyboardMarkup(keyboard)


def notebook_actions_keyboard(notebook_id: str) -> InlineKeyboardMarkup:
    """Keyboard with actions for a specific notebook."""
    keyboard = [
        [
            InlineKeyboardButton("💬 Query", callback_data=f"query_{notebook_id}"),
            InlineKeyboardButton("📄 Sources", callback_data=f"sources_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("🎙️ Audio", callback_data=f"audio_{notebook_id}"),
            InlineKeyboardButton("📊 Status", callback_data=f"status_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("🔗 Share", callback_data=f"share_{notebook_id}"),
            InlineKeyboardButton("📝 Notes", callback_data=f"notes_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="menu_notebooks"),
            InlineKeyboardButton("🏠 Main", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def studio_menu_keyboard(notebook_id: str) -> InlineKeyboardMarkup:
    """Keyboard for studio content creation."""
    keyboard = [
        [
            InlineKeyboardButton("🎙️ Audio", callback_data=f"create_audio_{notebook_id}"),
            InlineKeyboardButton("🎬 Video", callback_data=f"create_video_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("📊 Report", callback_data=f"create_report_{notebook_id}"),
            InlineKeyboardButton("📑 Slides", callback_data=f"create_slides_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("🗺️ Mind Map", callback_data=f"create_mindmap_{notebook_id}"),
            InlineKeyboardButton("🎴 Flashcards", callback_data=f"create_flashcards_{notebook_id}"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data=f"notebook_{notebook_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def sources_list_keyboard(notebook_id: str, sources: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard for viewing sources."""
    keyboard = []
    for src in sources[:8]:  # Limit to 8 sources
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {src.get('title', 'Untitled')[:25]}",
                callback_data=f"source_{notebook_id}_{src['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton("➕ Add URL", callback_data=f"add_url_{notebook_id}"),
        InlineKeyboardButton("➕ Add Text", callback_data=f"add_text_{notebook_id}"),
    ])
    keyboard.append([
        InlineKeyboardButton("◀️ Back", callback_data=f"notebook_{notebook_id}"),
    ])
    return InlineKeyboardMarkup(keyboard)


def confirm_delete_keyboard(notebook_id: str) -> InlineKeyboardMarkup:
    """Confirmation keyboard for delete action."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{notebook_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"notebook_{notebook_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def share_keyboard(notebook_id: str, is_public: bool) -> InlineKeyboardMarkup:
    """Keyboard for sharing options."""
    if is_public:
        keyboard = [
            [
                InlineKeyboardButton("🔗 Copy Link", callback_data=f"copy_link_{notebook_id}"),
            ],
            [
                InlineKeyboardButton("🔒 Make Private", callback_data=f"make_private_{notebook_id}"),
            ],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("🌍 Make Public", callback_data=f"make_public_{notebook_id}"),
            ],
        ]
    keyboard.append([
        InlineKeyboardButton("👥 Add Collaborator", callback_data=f"add_collab_{notebook_id}"),
    ])
    keyboard.append([
        InlineKeyboardButton("◀️ Back", callback_data=f"notebook_{notebook_id}"),
    ])
    return InlineKeyboardMarkup(keyboard)


def back_keyboard(callback_data: str = "menu_main") -> InlineKeyboardMarkup:
    """Simple back button keyboard."""
    keyboard = [
        [InlineKeyboardButton("◀️ Back", callback_data=callback_data)],
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel button keyboard."""
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def research_mode_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting research mode."""
    keyboard = [
        [
            InlineKeyboardButton("⚡ Fast (~30s, ~10 sources)", callback_data="research_mode_fast"),
        ],
        [
            InlineKeyboardButton("🔬 Deep (~5min, ~40 sources)", callback_data="research_mode_deep"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def research_source_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting research source type."""
    keyboard = [
        [
            InlineKeyboardButton("🌐 Web Search", callback_data="research_source_web"),
        ],
        [
            InlineKeyboardButton("📁 Google Drive", callback_data="research_source_drive"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="menu_research"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
