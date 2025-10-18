import logging
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.responses import Response
from auth import ZoomAuthenticator
from data.base import auth_token_context
import json

def initialise_sse(app: Server, sse: SseServerTransport, logger: logging.Logger, access_token: str) -> callable:


    async def handle_sse(request):
        """Handle SSE connection for MCP server."""
        logger.info("Handling SSE connection")
    
        # Set the auth token in context for this request
        token = auth_token_context.set(access_token)

        try:
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
            raise
        finally:
            auth_token_context.reset(token)
        
        return Response()

    return handle_sse

    