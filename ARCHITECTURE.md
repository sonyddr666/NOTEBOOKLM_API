# NotebookLM API + Telegram Bot Architecture

## Overview

This project extends the `notebooklm-mcp-cli` library to provide:
1. **REST API** - FastAPI-based HTTP API for external integrations
2. **Telegram Bot** - Full-featured bot for NotebookLM interactions
3. **Docker Deployment** - Containerized deployment with all dependencies

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL CLIENTS                                │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│   │ Telegram App │    │ HTTP Client  │    │ External Applications        │  │
│   │   (Users)    │    │  (Postman)   │    │ (Zapier, n8n, Custom Apps)   │  │
│   └──────┬───────┘    └──────┬───────┘    └──────────────┬───────────────┘  │
└──────────┼───────────────────┼───────────────────────────┼──────────────────┘
           │                   │                           │
           │                   │                           │
           ▼                   ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DOCKER CONTAINER                                │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         FASTAPI SERVER                               │   │
│   │                                                                      │   │
│   │   /api/v1/notebooks     - List, create, delete notebooks            │   │
│   │   /api/v1/notebooks/{id} - Get, rename, query notebooks             │   │
│   │   /api/v1/sources       - Add URL/text/drive/file sources           │   │
│   │   /api/v1/studio        - Create audio, video, reports, etc.        │   │
│   │   /api/v1/research      - Web/Drive research                        │   │
│   │   /api/v1/share         - Sharing and collaboration                 │   │
│   │   /api/v1/notes         - Note management                            │   │
│   │   /health               - Health check endpoint                      │   │
│   │                                                                      │   │
│   └──────────────────────────────┬──────────────────────────────────────┘   │
│                                  │                                           │
│                                  │                                           │
│   ┌──────────────────────────────┴──────────────────────────────────────┐   │
│   │                         TELEGRAM BOT                                 │   │
│   │                                                                      │   │
│   │   Commands:                                                          │   │
│   │   /start, /help        - Welcome and help                            │   │
│   │   /notebooks           - List all notebooks                          │   │
│   │   /create <title>      - Create new notebook                         │   │
│   │   /query <notebook>    - Chat with notebook                          │   │
│   │   /add <type> <value>  - Add source (url/text/file)                  │   │
│   │   /audio <notebook>    - Generate audio overview                     │   │
│   │   /status <notebook>   - Check studio status                         │   │
│   │   /share <notebook>    - Share notebook                              │   │
│   │                                                                      │   │
│   │   Features:                                                          │   │
│   │   - Inline keyboard navigation                                       │   │
│   │   - File upload support                                              │   │
│   │   - Conversation context memory                                      │   │
│   │   - Rate limiting per user                                           │   │
│   │                                                                      │   │
│   └──────────────────────────────┬──────────────────────────────────────┘   │
│                                  │                                           │
│                                  │                                           │
│   ┌──────────────────────────────┴──────────────────────────────────────┐   │
│   │                    NOTEBOOKLM CLIENT (Core)                          │   │
│   │                                                                      │   │
│   │   - Authentication (cookies, CSRF tokens)                            │   │
│   │   - Notebook CRUD operations                                         │   │
│   │   - Source management                                                │   │
│   │   - Studio content generation                                        │   │
│   │   - Research operations                                              │   │
│   │   - Sharing and collaboration                                        │   │
│   │                                                                      │   │
│   └──────────────────────────────┬──────────────────────────────────────┘   │
│                                  │                                           │
└──────────────────────────────────┼───────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GOOGLE NOTEBOOKLM API                                │
│                                                                              │
│   https://notebooklm.google.com (Internal RPC API)                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
notebooklm-api/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── notebooks.py      # Notebook endpoints
│   │   │   ├── sources.py        # Source management endpoints
│   │   │   ├── studio.py         # Studio content endpoints
│   │   │   ├── research.py       # Research endpoints
│   │   │   ├── sharing.py        # Sharing endpoints
│   │   │   ├── notes.py          # Notes endpoints
│   │   │   └── health.py         # Health check
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── notebooks.py      # Pydantic models
│   │   │   ├── sources.py
│   │   │   └── studio.py
│   │   └── dependencies.py       # Shared dependencies
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py               # Telegram bot main
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── start.py          # /start, /help handlers
│   │   │   ├── notebooks.py      # Notebook commands
│   │   │   ├── sources.py        # Source commands
│   │   │   ├── studio.py         # Studio commands
│   │   │   ├── chat.py           # Chat/query commands
│   │   │   └── callbacks.py      # Inline keyboard callbacks
│   │   ├── keyboards.py          # Inline keyboards
│   │   └── middleware.py         # Rate limiting, auth
│   └── core/
│       ├── __init__.py
│       ├── client.py             # NotebookLM client wrapper
│       └── exceptions.py         # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_bot.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── login.py                  # Authentication helper
│   └── start.sh                  # Startup script
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## API Endpoints

### Notebooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notebooks` | List all notebooks |
| POST | `/api/v1/notebooks` | Create a new notebook |
| GET | `/api/v1/notebooks/{id}` | Get notebook details |
| PUT | `/api/v1/notebooks/{id}` | Rename notebook |
| DELETE | `/api/v1/notebooks/{id}` | Delete notebook |
| POST | `/api/v1/notebooks/{id}/query` | Query notebook with AI |
| GET | `/api/v1/notebooks/{id}/summary` | Get AI-generated summary |

### Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notebooks/{id}/sources` | List sources |
| POST | `/api/v1/notebooks/{id}/sources` | Add source (url/text/drive/file) |
| DELETE | `/api/v1/notebooks/{id}/sources/{source_id}` | Delete source |
| POST | `/api/v1/notebooks/{id}/sources/{source_id}/sync` | Sync Drive source |

### Studio

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/notebooks/{id}/studio/audio` | Create audio overview |
| POST | `/api/v1/notebooks/{id}/studio/video` | Create video overview |
| POST | `/api/v1/notebooks/{id}/studio/infographic` | Create infographic |
| POST | `/api/v1/notebooks/{id}/studio/slide-deck` | Create slide deck |
| POST | `/api/v1/notebooks/{id}/studio/report` | Create report |
| POST | `/api/v1/notebooks/{id}/studio/flashcards` | Create flashcards |
| POST | `/api/v1/notebooks/{id}/studio/quiz` | Create quiz |
| POST | `/api/v1/notebooks/{id}/studio/mind-map` | Create mind map |
| GET | `/api/v1/notebooks/{id}/studio/status` | Get studio status |
| GET | `/api/v1/studio/artifacts/{artifact_id}/download` | Download artifact |

### Research

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/notebooks/{id}/research/start` | Start research |
| GET | `/api/v1/notebooks/{id}/research/{research_id}` | Poll research status |
| POST | `/api/v1/notebooks/{id}/research/{research_id}/import` | Import research sources |

### Sharing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notebooks/{id}/share` | Get share status |
| POST | `/api/v1/notebooks/{id}/share/public` | Enable public access |
| DELETE | `/api/v1/notebooks/{id}/share/public` | Disable public access |
| POST | `/api/v1/notebooks/{id}/share/collaborator` | Add collaborator |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notebooks/{id}/notes` | List notes |
| POST | `/api/v1/notebooks/{id}/notes` | Create note |
| PUT | `/api/v1/notebooks/{id}/notes/{note_id}` | Update note |
| DELETE | `/api/v1/notebooks/{id}/notes/{note_id}` | Delete note |

## Telegram Bot Commands

### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show welcome message |
| `/help` | Show available commands and usage |
| `/auth` | Check authentication status |

### Notebook Commands

| Command | Description |
|---------|-------------|
| `/notebooks` | List all notebooks with inline buttons |
| `/create <title>` | Create a new notebook |
| `/notebook <id>` | Show notebook details |
| `/rename <id> <title>` | Rename a notebook |
| `/delete <id>` | Delete a notebook (with confirmation) |

### Source Commands

| Command | Description |
|---------|-------------|
| `/sources <notebook_id>` | List sources in notebook |
| `/add_url <notebook_id> <url>` | Add URL as source |
| `/add_text <notebook_id> <text>` | Add text as source |
| `/upload <notebook_id>` | Upload file as source (reply with file) |
| `/delete_source <notebook_id> <source_id>` | Delete a source |

### Chat Commands

| Command | Description |
|---------|-------------|
| `/query <notebook_id> <question>` | Ask a question to notebook |
| `/chat <notebook_id>` | Start interactive chat mode |
| `/exit` | Exit chat mode |

### Studio Commands

| Command | Description |
|---------|-------------|
| `/audio <notebook_id>` | Generate audio overview |
| `/video <notebook_id>` | Generate video overview |
| `/report <notebook_id>` | Generate briefing report |
| `/slides <notebook_id>` | Generate slide deck |
| `/status <notebook_id>` | Check studio status |
| `/download <artifact_id>` | Download artifact |

### Sharing Commands

| Command | Description |
|---------|-------------|
| `/share <notebook_id>` | Show sharing options |
| `/public <notebook_id>` | Make notebook public |
| `/private <notebook_id>` | Make notebook private |

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. Initial Setup (One-time)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ Run login   │────▶│ Chrome      │────▶│ Extract     │
   │ script      │     │ opens       │     │ cookies     │
   └─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Save to     │
                                        │ .auth file  │
                                        └─────────────┘

2. API Request Flow
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ Client      │────▶│ API Server  │────▶│ Load cookies│
   │ Request     │     │ receives    │     │ from file   │
   └─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ NotebookLM  │
                                        │ API call    │
                                        └─────────────┘

3. Auto-Refresh (when expired)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ 401 Error   │────▶│ Headless    │────▶│ New cookies │
   │ detected    │     │ Chrome      │     │ saved       │
   └─────────────┘     └─────────────┘     └─────────────┘
```

## Docker Deployment

```yaml
# docker-compose.yml structure
services:
  notebooklm-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_KEY=${API_KEY}
    volumes:
      - ./data:/app/data  # Persist auth tokens
    restart: unless-stopped
```

## Security Considerations

1. **API Authentication**
   - API key for external access
   - Rate limiting per IP/key
   - Input validation with Pydantic

2. **Telegram Bot Security**
   - Rate limiting per user
   - Admin-only commands (optional)
   - User allowlist (optional)

3. **NotebookLM Authentication**
   - Cookies stored securely
   - Auto-refresh on expiration
   - Profile-based multi-account support

## Error Handling

```python
# Standard error response format
{
    "error": {
        "code": "NOTEBOOK_NOT_FOUND",
        "message": "Notebook with ID 'abc123' not found",
        "details": {}
    }
}
```

## Rate Limiting

| Endpoint Type | Rate Limit |
|---------------|------------|
| API (per key) | 100 req/min |
| Telegram (per user) | 30 msg/min |
| Studio creation | 5 per hour |

## Future Enhancements

1. **Webhook Support** - Notify external services on events
2. **Multi-user Support** - Separate auth per API user
3. **WebSocket** - Real-time studio status updates
4. **OAuth Integration** - Google OAuth for authentication
5. **Caching** - Redis for response caching
