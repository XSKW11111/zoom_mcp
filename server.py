import contextlib
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from starlette.routing import Mount
import uvicorn
import logging
import sys
import click

# Import zoom_mcp instance from base
from base import zoom_mcp

# Import tools to register them with zoom_mcp
# This import is CRITICAL - it executes the @zoom_mcp.tool() decorators
from tools.meeting import *


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(zoom_mcp.session_manager.run())
        yield


def configure_logging(log_level: str):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


@click.command()
@click.option("--port", type=int, default=8000, help="Port to run the server on")
@click.option("--log-level", type=str, default="INFO", help="Log level")
def main(port: int, log_level: str):
    configure_logging(log_level)

    logger = logging.getLogger(__name__)

    routes = [
        Mount("/sse", app=zoom_mcp.sse_app()),
        Mount("/mcp", app=zoom_mcp.streamable_http_app()),
    ]

    starlette_app = Starlette(routes=routes, lifespan=lifespan)

    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Configure appropriately for production
        allow_methods=["GET", "POST", "DELETE"],  # MCP streamable HTTP methods
        expose_headers=["Mcp-Session-Id"],
    )

    try:
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
        logger.info("Server started on port 8000")
    except Exception as e:
        logger.error("Error starting server: %s", e)
        sys.exit(1)
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
