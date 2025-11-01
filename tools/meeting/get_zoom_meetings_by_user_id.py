from base import ZOOM_API_BASE_URL, zoom_mcp
from auth import get_access_token
import aiohttp
from errorUtils import _extract_error_message
import logging

logger = logging.getLogger(__name__)


@zoom_mcp.tool()
async def get_zoom_meetings_by_user_id(user_id: str) -> list[dict]:
    """Fetch meetings for a Zoom user by their user ID.

    Args:
        user_id: The Zoom user ID to fetch meetings for

    Returns:
        List of meetings for the specified user
    """

    # Get access token
    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
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

                raise Exception(message)
            logger.info(f"Zoom meetings for user '{user_id}': {payload}")
            return payload
