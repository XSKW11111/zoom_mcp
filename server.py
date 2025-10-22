#!/usr/bin/env python3
"""Entrypoint for the Zoom MCP server using an SSE transport."""

from __future__ import annotations

import asyncio
import logging
import sys
import uvicorn
from contextlib import asynccontextmanager
import aiohttp

import click
from dotenv import load_dotenv

from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
import mcp.types as types

from starlette.routing import Mount, Route
from starlette.applications import Starlette

from transport.sse import initialise_sse
from transport.streamable_http import initialise_streamable_http
from auth import get_access_token
from data import get_zoom_meetings_by_user_id

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
        asyncio.run(get_access_token())
    except Exception as e:
        logger.error("Error getting access token: %s", e)

    logger.info("Authenticated successfully")

    handle_sse = initialise_sse(app, sse, logger)


    # Set up StreamableHTTP transport
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # Stateless mode - can be changed to use an event store
        json_response=json_response,
        stateless=True,
    )
    
    handle_streamable_http = initialise_streamable_http(session_manager, logger)

    routes = [
        # SSE transport
        Route("/sse", endpoint=handle_sse),
        Mount("/message", app=sse.handle_post_message),
        # StreamableHTTP transport - handle both /mcp and /mcp/
        Mount("/mcp", app=handle_streamable_http)
    ]

    @asynccontextmanager
    async def lifespan(app: Starlette):
        app.state.http = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20),
            connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300),
            headers={"User-Agent": "zoom-mcp/0.1"}
        )
            # Initialize the StreamableHTTP session manager
        async with session_manager.run():
            logger.info("Application started with dual transport (StreamableHTTP)")
            try:
                yield
            finally:
                await app.state.http.close()

    starlette_app = Starlette(routes=routes, lifespan=lifespan)


    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_zoom_meetings_by_user_id",
                description="Get Zoom meetings for a given user ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to get Zoom meetings for"
                        }
                    },
                    "required": ["user_id"]
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool(tool_name: str, args: dict) -> types.CallToolResult:
        try:
            if tool_name == "get_zoom_meetings_by_user_id":
                return await get_zoom_meetings_by_user_id(app, **args)
        except Exception as e:
            logger.error("Error calling tool: %s", e)
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Error calling tool: {e}")])

    try:
        uvicorn.run(
               starlette_app,
               host="0.0.0.0",
              port=port,
              log_level=log_level.lower(),
            )
    except Exception as e:
        logging.error("Error starting server: %s", e)
        sys.exit(1)
    finally:
        logging.info("Server stopped")

if __name__ == "__main__":
    main()
    