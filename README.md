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

3. Update `.env` with your configuration

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

The project is organized into:
- `server/core.py` - connect handler to tool in mcp_server
- `server/tools/` & `server/resources/` – namespaces for future Zoom integrations.

To flesh out the integration:

1. Implement concrete tool/resource handlers in the respective packages.
2. Wire those handlers into `server/core.py`.
3. Flesh out the SSE endpoints to forward events and tool invocations between clients and the MCP server.

## License

MIT License
