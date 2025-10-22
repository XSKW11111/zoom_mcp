import logging
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Scope, Receive, Send
from starlette.responses import PlainTextResponse

def initialise_streamable_http(session_manager: StreamableHTTPSessionManager, logger: logging.Logger) -> callable:
    
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        logger.info("Handling StreamableHTTP request")
        
        # Set the auth token in context for this request
        try:
            await session_manager.handle_request(scope, receive, send)
        except Exception as e:
            logger.error(f"Error handling StreamableHTTP request: {e}")
            raise

    return handle_streamable_http
