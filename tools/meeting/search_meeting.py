from base import ZOOM_API_BASE_URL, zoom_mcp
from auth import get_access_token
import aiohttp
from errorUtils import _extract_error_message


@zoom_mcp.tool()
async def search_meeting(
    query: str,
    page_size: int = 30,
    next_page_token: str | None = None,
) -> dict:
    """Search meetings at the account level.

    Args:
        query: Search query string
        page_size: Items per page (Zoom defaults apply; max may be enforced by API)
        next_page_token: Token for paginated results

    Returns:
        Zoom search response containing meetings and pagination tokens
    """

    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params: dict[str, str | int] = {"query": query, "page_size": page_size}
    if next_page_token:
        params["next_page_token"] = next_page_token

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ZOOM_API_BASE_URL}/search/meetings",
            headers=headers,
            params=params,
        ) as response:
            payload = await response.json()

            if response.status >= 400:
                error_detail = _extract_error_message(payload) or response.reason
                message = f"Failed to search meetings (HTTP {response.status})"
                if error_detail:
                    message = f"{message}: {error_detail}"
                raise Exception(message)

            return payload
