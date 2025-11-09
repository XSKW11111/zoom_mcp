import asyncio

import pytest

from auth import ZoomAuthError, ZoomAuthenticator


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


def test_get_user_returns_cached(monkeypatch):
    async def _run():
        auth = ZoomAuthenticator("acct", "id", "secret")
        auth._user_cache = {"id": "user123"}

        async def _fail():
            raise AssertionError(
                "get_access_token should not be called when cache populated"
            )

        monkeypatch.setattr(auth, "get_access_token", _fail)

        result = await auth.get_user()
        assert result == {"id": "user123"}

    asyncio.run(_run())


def test_get_user_fetches_and_caches(monkeypatch):
    async def _run():
        payload = {"id": "zoom-user"}
        factory = _SessionFactory(_DummyResponse(payload))
        monkeypatch.setattr("auth.aiohttp.ClientSession", factory)

        auth = ZoomAuthenticator("acct", "id", "secret")

        async def _fake_get_access_token():
            return "token"

        monkeypatch.setattr(auth, "get_access_token", _fake_get_access_token)

        first = await auth.get_user()
        second = await auth.get_user()

        assert first == payload
        assert second is first  # cached object reused
        assert factory.instances == 1

    asyncio.run(_run())


def test_get_user_id_requires_id():
    async def _run():
        auth = ZoomAuthenticator("acct", "id", "secret")
        auth._user_cache = {}

        with pytest.raises(ZoomAuthError):
            await auth.get_user_id()

    asyncio.run(_run())


def test_get_user_raises_on_http_error(monkeypatch):
    async def _run():
        payload = {"message": "not authorized"}
        factory = _SessionFactory(
            _DummyResponse(payload, status=401, reason="Unauthorized")
        )
        monkeypatch.setattr("auth.aiohttp.ClientSession", factory)

        auth = ZoomAuthenticator("acct", "id", "secret")

        async def _fake_get_access_token():
            return "token"

        monkeypatch.setattr(auth, "get_access_token", _fake_get_access_token)

        with pytest.raises(ZoomAuthError) as exc:
            await auth.get_user()

        assert "Failed to fetch user" in str(exc.value)

    asyncio.run(_run())
