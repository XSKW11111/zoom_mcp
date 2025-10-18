import logging
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.responses import Response

def initialise_sse(app: Server, sse: SseServerTransport, logger: logging.Logger) -> callable:


    async def handle_sse(request):
        """Handle SSE connection for MCP server."""
        logger.info("Handling SSE connection")
    
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
        
        return Response()

    return handle_sse

    