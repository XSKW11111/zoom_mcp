import logging
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Scope, Receive, Send

from auth import ZoomAuthenticator
from data.base import auth_token_context

def initialise_streamable_http(app: Server, session_manager: StreamableHTTPSessionManager, logger: logging.Logger, access_token: str) -> callable:
    
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        logger.info("Handling StreamableHTTP request")
        
        # Extract auth token from headers
        print(f"Access token: {access_token}")
        logger.info(f"Access token: {access_token}")
        
        # Set the auth token in context for this request
        token = auth_token_context.set(access_token)
        try:
            await session_manager.handle_request(scope, receive, send)
        finally:
            auth_token_context.reset(token)

    return handle_streamable_http
