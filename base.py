from mcp.server.fastmcp import FastMCP

# Context variable to store the access token for each request
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

# Initialize FastMCP instance
zoom_mcp = FastMCP("zoom-mcp-server", stateless_http=True, streamable_http_path="/")
