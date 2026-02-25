# NotebookLM API & Telegram Bot

A comprehensive REST API and Telegram Bot for Google NotebookLM, built on top of [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli).

## Features

### 🌐 REST API
- Full NotebookLM functionality via HTTP endpoints
- OpenAPI/Swagger documentation
- API key authentication
- Rate limiting
- Health checks for load balancers

### 🤖 Telegram Bot
- Interactive inline keyboards
- Chat mode for conversations with notebooks
- File upload support
- Rate limiting per user
- User allowlist support

### 📚 Supported Operations
- **Notebooks**: Create, list, rename, delete
- **Sources**: Add URLs, text, Google Drive, files
- **Query**: AI-powered Q&A with notebooks
- **Studio**: Generate audio podcasts, videos, reports, slides, mind maps
- **Research**: Web and Drive research
- **Sharing**: Public links and collaborators
- **Notes**: Create and manage notes

## Quick Start

### Prerequisites
- Python 3.11+
- Google account with NotebookLM access
- Telegram bot token (optional, for bot)

### 1. Clone and Install

```bash
# Clone this repository
git clone <your-repo-url>
cd NOTEBOOKLM_API

# The notebooklm-mcp-cli is already cloned in the repository

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Authenticate with NotebookLM

```bash
# Install the CLI tool
pip install -e ./notebooklm-mcp-cli

# Login to Google (opens Chrome for authentication)
nlm login

# Verify authentication
nlm login --check
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

Required configuration:
```env
# For Telegram bot
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather

# For API authentication (optional)
API_KEY=your-secret-api-key
```

### 4. Run

**Option A: Run API only**
```bash
python -m src.api.main
```

**Option B: Run Telegram bot only**
```bash
python -m src.bot.main
```

**Option C: Run both with Docker**
```bash
docker-compose up -d
```

## API Documentation

Once the API is running, access the documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notebooks` | List all notebooks |
| POST | `/api/v1/notebooks` | Create a notebook |
| GET | `/api/v1/notebooks/{id}` | Get notebook details |
| PUT | `/api/v1/notebooks/{id}` | Rename notebook |
| DELETE | `/api/v1/notebooks/{id}` | Delete notebook |
| POST | `/api/v1/notebooks/{id}/query` | Query with AI |
| GET | `/api/v1/notebooks/{id}/sources` | List sources |
| POST | `/api/v1/notebooks/{id}/sources` | Add source |
| POST | `/api/v1/notebooks/{id}/studio/audio` | Create audio |
| POST | `/api/v1/notebooks/{id}/studio/video` | Create video |
| GET | `/api/v1/notebooks/{id}/studio/status` | Check status |
| GET | `/health` | Health check |

### Example API Calls

```bash
# List notebooks
curl http://localhost:8000/api/v1/notebooks

# Create a notebook
curl -X POST http://localhost:8000/api/v1/notebooks \
  -H "Content-Type: application/json" \
  -d '{"title": "My Research"}'

# Query a notebook
curl -X POST http://localhost:8000/api/v1/notebooks/{id}/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics?"}'

# Generate audio overview
curl -X POST http://localhost:8000/api/v1/notebooks/{id}/studio/audio
```

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help |
| `/notebooks` | List notebooks |
| `/create <title>` | Create notebook |
| `/notebook <id>` | View notebook |
| `/query <id> <question>` | Ask question |
| `/chat <id>` | Interactive chat mode |
| `/audio <id>` | Generate audio |
| `/status <id>` | Check studio status |
| `/share <id>` | Sharing options |
| `/auth` | Check auth status |

## Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### With Redis (optional)

```bash
docker-compose --profile redis up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `API_KEY` | API authentication key | None |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `TELEGRAM_ADMIN_USERS` | Admin user IDs | None |
| `NOTEBOOKLM_PROFILE` | Auth profile | `default` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Project Structure

```
notebooklm-api/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── routes/       # API endpoints
│   │   └── schemas/      # Pydantic models
│   ├── bot/              # Telegram bot
│   │   ├── handlers/     # Command handlers
│   │   └── keyboards.py  # Inline keyboards
│   └── core/             # Core functionality
│       ├── client.py     # NotebookLM client wrapper
│       └── exceptions.py # Custom exceptions
├── docker/
│   └── Dockerfile
├── scripts/
│   └── start.sh
├── notebooklm-mcp-cli/   # Cloned library
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Authentication Flow

1. Run `nlm login` to authenticate with Google
2. Cookies are stored in `~/.notebooklm-mcp-cli/`
3. API/Bot automatically loads cookies on startup
4. If cookies expire, re-run `nlm login`

## Troubleshooting

### Authentication Errors
```bash
# Check auth status
nlm login --check

# Re-authenticate
nlm login
```

### Bot Not Responding
1. Check `TELEGRAM_BOT_TOKEN` is set correctly
2. Verify bot is not blocked by user
3. Check logs for errors

### API Returns 401
1. If `API_KEY` is set, include `X-API-Key` header
2. Check NotebookLM authentication

## Security Notes

- Store `.env` securely and never commit it
- Use `API_KEY` for production deployments
- Configure `TELEGRAM_ALLOWED_USERS` to restrict bot access
- Run behind reverse proxy with HTTPS in production

## Credits

- Built on [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) by Jacob Ben-David
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- Uses [python-telegram-bot](https://python-telegram-bot.org/) for the Telegram bot

## License

MIT License - See LICENSE file for details.
