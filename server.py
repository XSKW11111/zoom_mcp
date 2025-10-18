#!/usr/bin/env python3
"""Entrypoint for the Zoom MCP server using an SSE transport."""

from __future__ import annotations

import asyncio
import json
import logging
import uvicorn

from dotenv import load_dotenv

import click
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import CallToolResult, ListToolsResult, Tool

from starlette.routing import Mount, Route
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.types import Scope, Receive, Send

from transport.sse import initialise_sse
from transport.streamable_http import initialise_streamable_http
from auth import get_access_token

def configure_logging() -> None:
    """Apply basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

@click.command()
@click.option("--port", type=int, default=8000, help="Port to run the server on")
@click.option("--log-level", type=str, default="INFO", help="Log level")
@click.option("--json-response", type=bool, is_flag=True, default=False, help="Use JSON response")
def main(port: int, log_level: str, json_response: bool) -> None:
    """Configure environment and launch the SSE transport."""
    load_dotenv()
    configure_logging()

    logger = logging.getLogger(__name__)

    # Create MCP server directly
    app = Server("zoom-mcp-server")
    
    sse = SseServerTransport('/message')

    try:
        access_token = asyncio.run(get_access_token())
    except Exception as e:
        logger.error(f"Error getting access token: {e}")

    logger.info(f"Authenticated successfully")

    handle_sse = initialise_sse(app, sse, logger, access_token)


    # Set up StreamableHTTP transport
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # Stateless mode - can be changed to use an event store
        json_response=json_response,
        stateless=True,
    )
    
    handle_streamable_http = initialise_streamable_http(app, session_manager, logger, access_token)

    routes = [
        # SSE transport
        Route("/sse", endpoint=handle_sse),
        Mount("/message", app=sse.handle_post_message),
        # StreamableHTTP transport
        Mount("/mcp", app=handle_streamable_http)
    ]

    starlette_app = Starlette(routes=routes)

    try:
        uvicorn.run(
               starlette_app,
               host="0.0.0.0",
              port=port,
              log_level=log_level.lower(),
            )
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        logging.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
    