# Zoom MCP Server

Skeleton project for a Model Context Protocol (MCP) server that will integrate with Zoom.
It currently exposes a Server-Sent Events (SSE) transport and placeholder MCP handlers,
ready for Zoom-specific logic to be wired in.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Fill `.env` with your Zoom server-to-server OAuth credentials.

## Usage

### Running the SSE Transport

```bash
python server.py
```

### MCP Client Configuration (example)

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "zoom-mcp": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "MCP_SERVER_NAME": "zoom-mcp",
        "MCP_SERVER_VERSION": "1.0.0"
      }
    }
  }
}
```

## Development

The current modules of interest are:
- `server.py` – entry point that wires the FastMCP transports into Starlette/uvicorn.
- `base.py` – FastMCP instance and shared constants (e.g., Zoom API base URL).
- `auth.py` – server-to-server OAuth helper that caches the current account’s token and profile.
- `tools/meeting/` – MCP tool implementations that call Zoom meeting APIs.

To add Zoom functionality:

1. Implement new tool functions under `tools/` and decorate them with `@zoom_mcp.tool()`.
2. Import the new tools somewhere under `server.py` so the decorators run at startup.
3. Extend `auth.py` or add helper modules as needed for additional Zoom endpoints.

## License

MIT License
