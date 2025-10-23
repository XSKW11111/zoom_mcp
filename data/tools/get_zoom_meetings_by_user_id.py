from data.base import ZOOM_API_BASE_URL
from data.base import send_auth_request
import mcp.types as types
from starlette.applications import Starlette


@send_auth_request
async def get_zoom_meetings_by_user_id(
    app: Starlette,
    user_id: str,
    access_token: str,
) -> types.CallToolResult:
    """Fetch meetings for a user and package the payload for MCP transport.

    The MCP server expects tool functions to return a ``CallToolResult`` whose
    ``content`` list contains serialisable ``Content`` instances.  Successful
    responses therefore wrap the Zoom API payload in ``JsonContent`` while
    non-2xx responses are converted into ``TextContent`` errors to avoid
    leaking stack traces to the client.
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with app.state.http.get(
        f"{ZOOM_API_BASE_URL}/users/{user_id}/meetings",
        headers=headers,
    ) as response:
        payload = await response.json()

        if response.status >= 400:
            error_detail = _extract_error_message(payload) or response.reason
            message = (
                f"Failed to fetch meetings for user '{user_id}'"
                f" (HTTP {response.status})"
            )
            if error_detail:
                message = f"{message}: {error_detail}"

            return types.CallToolResult(
                isError=True,
                content=[
                    types.TextContent(type="text", text=message),
                ],
            )

        return types.CallToolResult(
            content=[
                types.JsonContent(type="json", json=payload),
            ]
        )


def _extract_error_message(payload: object) -> str | None:
    """Pull a human-readable error message out of the Zoom API payload."""

    if isinstance(payload, dict):
        for key in ("message", "error", "errorMessage"):
            if key in payload and payload[key]:
                return str(payload[key])

    return None
