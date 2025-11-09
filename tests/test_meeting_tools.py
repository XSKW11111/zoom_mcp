import asyncio

import pytest

from tools.meeting.get_own_zoom_meetings import get_own_zoom_meetings
from tools.meeting.get_zoom_meetings_by_user_id import get_zoom_meetings_by_user_id


class _DummyResponse:
    def __init__(self, payload, status=200, reason="OK"):
        self._payload = payload
        self.status = status
        self.reason = reason

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _DummySession:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, *args, **kwargs):
        return self._response


class _SessionFactory:
    def __init__(self, response):
        self.response = response
        self.instances = 0

    def __call__(self, *args, **kwargs):
        self.instances += 1
        return _DummySession(self.response)


def test_get_zoom_meetings_by_user_id_returns_payload(monkeypatch):
    async def _run():
        payload = {"meetings": [{"id": "123"}], "page_count": 1}
        factory = _SessionFactory(_DummyResponse(payload))
        monkeypatch.setattr(
            "tools.meeting.get_zoom_meetings_by_user_id.aiohttp.ClientSession", factory
        )

        async def _fake_get_access_token():
            return "token"

        monkeypatch.setattr(
            "tools.meeting.get_zoom_meetings_by_user_id.get_access_token",
            _fake_get_access_token,
        )

        result = await get_zoom_meetings_by_user_id("user123")

        assert result == payload
        assert factory.instances == 1

    asyncio.run(_run())


def test_get_zoom_meetings_by_user_id_raises_on_error(monkeypatch):
    async def _run():
        payload = {"message": "not found"}
        factory = _SessionFactory(
            _DummyResponse(payload, status=404, reason="Not Found")
        )
        monkeypatch.setattr(
            "tools.meeting.get_zoom_meetings_by_user_id.aiohttp.ClientSession", factory
        )

        async def _fake_get_access_token():
            return "token"

        monkeypatch.setattr(
            "tools.meeting.get_zoom_meetings_by_user_id.get_access_token",
            _fake_get_access_token,
        )

        with pytest.raises(Exception) as exc:
            await get_zoom_meetings_by_user_id("user123")

        assert "Failed to fetch meetings" in str(exc.value)

    asyncio.run(_run())


def test_get_own_zoom_meetings_uses_user_id(monkeypatch):
    async def _run():
        async def _fake_get_user_id():
            return "user123"

        async def _fake_get_meetings(user_id: str):
            assert user_id == "user123"
            return {"meetings": []}

        monkeypatch.setattr(
            "tools.meeting.get_own_zoom_meetings.get_user_id", _fake_get_user_id
        )
        monkeypatch.setattr(
            "tools.meeting.get_own_zoom_meetings.get_zoom_meetings_by_user_id",
            _fake_get_meetings,
        )

        result = await get_own_zoom_meetings()
        assert result == {"meetings": []}

    asyncio.run(_run())
