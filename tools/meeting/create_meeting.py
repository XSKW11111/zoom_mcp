from base import ZOOM_API_BASE_URL, zoom_mcp
from auth import get_access_token
import aiohttp
from errorUtils import _extract_error_message


@zoom_mcp.tool()
async def create_meeting(
    user_id: str,
    topic: str | None = None,
    start_time: str | None = None,
    duration: int | None = None,
    timezone: str | None = None,
    type: int | None = None,
    settings: dict | None = None,
) -> dict:
    """Create a Zoom meeting for a given user.

    Args:
        user_id: Zoom user ID or email for whom to create the meeting
        topic: Meeting topic/title
        start_time: ISO 8601 datetime string, e.g. '2025-10-30T15:00:00Z'
        duration: Duration in minutes
        timezone: IANA timezone name (e.g., 'America/Los_Angeles')
        type: Zoom meeting type (1=instant, 2=scheduled, 8=recurring w/ fixed time)
        settings: Additional Zoom meeting settings object

    Returns:
        Created meeting object
    """

    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    body: dict = {}
    if topic is not None:
        body["topic"] = topic
    if start_time is not None:
        body["start_time"] = start_time
    if duration is not None:
        body["duration"] = duration
    if timezone is not None:
        body["timezone"] = timezone
    if type is not None:
        body["type"] = type
    if settings is not None:
        body["settings"] = settings

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ZOOM_API_BASE_URL}/users/{user_id}/meetings",
            headers=headers,
            json=body,
        ) as response:
            payload = await response.json()

            if response.status >= 400:
                error_detail = _extract_error_message(payload) or response.reason
                message = (
                    f"Failed to create meeting for user '{user_id}'"
                    f" (HTTP {response.status})"
                )
                if error_detail:
                    message = f"{message}: {error_detail}"
                raise Exception(message)

            return payload
