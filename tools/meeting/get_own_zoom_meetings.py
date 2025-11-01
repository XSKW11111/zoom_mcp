from base import zoom_mcp
from auth import get_user_id
from .get_zoom_meetings_by_user_id import get_zoom_meetings_by_user_id


@zoom_mcp.tool()
async def get_own_zoom_meetings() -> list[dict]:
    user_id = await get_user_id()
    """Get the meetings for the current user."""
    return await get_zoom_meetings_by_user_id(user_id)
