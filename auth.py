"""Zoom server-to-server OAuth authentication module."""

import base64
import os
import time
from typing import Optional

import aiohttp
from base import ZOOM_API_BASE_URL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Zoom OAuth configuration
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
ZOOM_AUTH_BASE_URL = "https://zoom.us/oauth"


class ZoomAuthError(Exception):
    """Custom exception for Zoom authentication errors."""

    pass


class ZoomAuthenticator:
    """Handles Zoom server-to-server OAuth authentication."""

    def __init__(self, account_id: str, client_id: str, client_secret: str):
        """Initialize with Zoom OAuth credentials."""
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._user_cache: Optional[dict] = None

    def _get_basic_auth_header(self) -> str:
        """Generate Basic Auth header for Zoom API."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if (
            self._access_token
            and self._token_expires_at
            and time.time() < self._token_expires_at
        ):
            return self._access_token

        await self._refresh_access_token()
        return self._access_token

    async def _refresh_access_token(self) -> None:
        """Refresh the access token using server-to-server OAuth."""
        auth_url = f"{ZOOM_AUTH_BASE_URL}/token"
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "account_credentials", "account_id": self.account_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ZoomAuthError(
                        f"Failed to get access token: {response.status} - {error_text}"
                    )

                token_data = await response.json()
                self._access_token = token_data["access_token"]
                # Set expiration time (subtract 60 seconds for safety margin)
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 60

    async def get_user(self) -> dict:
        """Fetch and cache the Zoom user linked to this authenticator."""

        if self._user_cache is not None:
            return self._user_cache

        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ZOOM_API_BASE_URL}/users/me",
                headers=headers,
            ) as response:
                payload = await response.json()

                if response.status >= 400:
                    # Store negative result? Prefer not to cache errors.
                    message = payload.get("message") or response.reason
                    raise ZoomAuthError(
                        f"Failed to fetch user (HTTP {response.status}): {message}"
                    )

                self._user_cache = payload
                return payload

    async def get_user_id(self) -> str:
        """Return the Zoom user id tied to this authenticator."""
        user = await self.get_user()
        user_id = user.get("id") if isinstance(user, dict) else None
        if not user_id:
            raise ZoomAuthError("Zoom user object missing 'id'")
        return user_id


# Global authenticator instance
_authenticator: Optional[ZoomAuthenticator] = None


def get_authenticator() -> ZoomAuthenticator:
    """Get the global Zoom authenticator instance."""
    global _authenticator
    if _authenticator is None:
        if not all([ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET]):
            raise ZoomAuthError(
                "Missing Zoom OAuth credentials. Please set ZOOM_ACCOUNT_ID, "
                "ZOOM_CLIENT_ID, and ZOOM_CLIENT_SECRET environment variables."
            )
        _authenticator = ZoomAuthenticator(
            ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
        )
    return _authenticator


async def get_access_token() -> str:
    """Convenience function to get a valid access token."""
    return await get_authenticator().get_access_token()


async def get_user() -> dict:
    """Convenience function to get a Zoom user object, cached."""
    return await get_authenticator().get_user()


async def get_user_id() -> str:
    """Convenience function to resolve an identifier (id or email) to the user id."""
    return await get_authenticator().get_user_id()
