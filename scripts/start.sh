#!/bin/bash
# Startup script for NotebookLM API and Telegram Bot

set -e

echo "🚀 NotebookLM API & Telegram Bot"
echo "================================="

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check authentication
echo "🔐 Checking NotebookLM authentication..."
if [ ! -d ~/.notebooklm-mcp-cli ]; then
    echo "⚠️  NotebookLM not authenticated!"
    echo "   Please run: nlm login"
    echo "   Or: python scripts/login.py"
    exit 1
fi

# Determine what to run
MODE=${1:-"all"}

case $MODE in
    api)
        echo "🌐 Starting API server..."
        python -m src.api.main
        ;;
    bot)
        echo "🤖 Starting Telegram bot..."
        python -m src.bot.main
        ;;
    all)
        echo "🌐 Starting API server and Telegram bot..."
        
        # Start API in background
        python -m src.api.main &
        API_PID=$!
        
        # Wait for API to be ready
        sleep 5
        
        # Start bot
        python -m src.bot.main &
        BOT_PID=$!
        
        # Handle shutdown
        trap "kill $API_PID $BOT_PID 2>/dev/null" EXIT
        
        # Wait for processes
        wait
        ;;
    *)
        echo "Usage: $0 [api|bot|all]"
        exit 1
        ;;
esac
