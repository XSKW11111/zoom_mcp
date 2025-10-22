import aiohttp
from data.base import send_auth_request
from data.base import ZOOM_API_BASE_URL
import mcp
from starlette.applications import Starlette


@send_auth_request
async def get_zoom_meetings_by_user_id(app: Starlette, user_id: str, access_token: str) -> list[dict]:
    """Get Zoom meetings for a given query."""

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with app.state.http.get(f"{ZOOM_API_BASE_URL}/users/{user_id}/meetings", headers=headers) as response:
            return await response.json()