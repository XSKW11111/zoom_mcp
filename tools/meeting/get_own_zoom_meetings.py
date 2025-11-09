from base import zoom_mcp
from auth import get_user_id
from .get_zoom_meetings_by_user_id import get_zoom_meetings_by_user_id


@zoom_mcp.tool()
async def get_own_zoom_meetings() -> dict:
    """Get the current authenticated user's meetings payload."""

    user_id = await get_user_id()
    return await get_zoom_meetings_by_user_id(user_id)
