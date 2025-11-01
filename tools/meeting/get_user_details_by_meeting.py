from base import ZOOM_API_BASE_URL, zoom_mcp
from auth import get_access_token
import aiohttp
from errorUtils import _extract_error_message


@zoom_mcp.tool()
async def get_user_details_by_meeting(meeting_id: str) -> dict:
    """Fetch host user details for a given meeting.

    Flow:
      1) GET /meetings/{meetingId} to obtain host_id
      2) GET /users/{host_id} to fetch host profile/details

    Args:
        meeting_id: The Zoom meeting ID

    Returns:
        Host user object
    """

    access_token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        # Fetch meeting to get host_id
        async with session.get(
            f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}", headers=headers
        ) as meeting_resp:
            meeting_payload = await meeting_resp.json()

            if meeting_resp.status >= 400:
                error_detail = (
                    _extract_error_message(meeting_payload) or meeting_resp.reason
                )
                message = (
                    f"Failed to fetch meeting '{meeting_id}'"
                    f" (HTTP {meeting_resp.status})"
                )
                if error_detail:
                    message = f"{message}: {error_detail}"
                raise Exception(message)

            host_id = meeting_payload.get("host_id")
            if not host_id:
                raise Exception("Meeting payload missing 'host_id'")

        # Fetch host user details
        async with aiohttp.ClientSession() as session2:
            async with session2.get(
                f"{ZOOM_API_BASE_URL}/users/{host_id}", headers=headers
            ) as user_resp:
                user_payload = await user_resp.json()

                if user_resp.status >= 400:
                    error_detail = (
                        _extract_error_message(user_payload) or user_resp.reason
                    )
                    message = (
                        f"Failed to fetch user '{host_id}' (HTTP {user_resp.status})"
                    )
                    if error_detail:
                        message = f"{message}: {error_detail}"
                    raise Exception(message)

                return user_payload
