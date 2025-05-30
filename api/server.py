import asyncio
import logging

import uvicorn

from api.app import app


async def run_api_server(host="127.0.0.1", port=8000):
    """
    Run the FastAPI server for external calls.

    Args:
        host (str): Host to bind the server to
        port (int): Port to bind the server to
    """
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    logging.info(f"✅ Starting FastAPI server on {host}:{port}")
    await server.serve()


def run_api_server_in_thread():
    """
    Run the FastAPI server in a separate thread.
    This function is used to run the server alongside the Telegram bot.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_api_server())
