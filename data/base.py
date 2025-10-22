import asyncio
from typing import Callable
from auth import get_access_token
# Context variable to store the access token for each request
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

def send_auth_request(func: Callable) -> Callable:

    async def wrapper(*args, **kwargs):
        access_token = await get_access_token()
        return await func(*args, **kwargs, access_token=access_token)

    return wrapper