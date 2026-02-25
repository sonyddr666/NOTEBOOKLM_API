"""Main entry point for NotebookLM API and Bot."""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NotebookLM API and Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "command",
        choices=["api", "bot", "all"],
        help="What to run: api, bot, or all"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    if args.command == "api":
        from src.api.main import run
        run()
    
    elif args.command == "bot":
        from src.bot.main import run_bot
        run_bot()
    
    elif args.command == "all":
        import asyncio
        import multiprocessing
        
        # Run API in a separate process
        api_process = multiprocessing.Process(
            target=_run_api,
            kwargs={"host": args.host, "port": args.port}
        )
        api_process.start()
        
        # Run bot in main process
        try:
            from src.bot.main import run_bot
            run_bot()
        except KeyboardInterrupt:
            pass
        finally:
            api_process.terminate()
            api_process.join()


def _run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run API server."""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
