from typing import List
from urllib.parse import urlencode

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from httpx import AsyncClient
from hypothesis import given, settings
from hypothesis.provisional import urls
from hypothesis.strategies import emails, permutations, text
from starlette import status
from tekore import scope as spotify_scope  # type: ignore[import]
from tekore._auth.expiring.client import OAUTH_AUTHORIZE_URL  # type: ignore[import]

from melodiam import conf
from melodiam.auth import Token, api

scope = None
user_id = None
code = "123456"


@api.get("/session")
async def return_session(request: Request) -> JSONResponse:
    return JSONResponse(request.session)


@api.get("/authorize")
async def authorize_mock(redirect_uri: str, state: str) -> RedirectResponse:
    query = {"code": code, "state": state}
    return RedirectResponse(f"{redirect_uri}?{urlencode(query)}")


@api.post("/api/token")
async def api_token_mock() -> JSONResponse:
    return JSONResponse(
        {
            "access_token": "123456",
            "token_type": "Bearer",
            "scope": scope,
            "expires_in": 3600,
            "refresh_token": "123456",
        }
    )


@api.get("/v1/me")
async def current_user_mock() -> JSONResponse:
    return JSONResponse(
        {
            "id": user_id,
            "href": "",
            "type": "user",
            "uri": "",
            "external_urls": {"spotify": ""},
        }
    )


@given(
    state=text(),
    next_url=urls(),
    user=emails(),
    scopes=permutations(list(spotify_scope.every)),
)  # type: ignore
@settings(deadline=800)  # type: ignore
@pytest.mark.asyncio
async def test_full_auth_sequence(
    state: str, next_url: str, user: str, scopes: List[str], auth_client: AsyncClient
) -> None:
    global scope, user_id
    scope = " ".join(sorted(scopes))
    user_id = user
    auth_client.cookies.clear()
    # Check initial /login redirection to mocked Spotify OAuth
    login_params = {"scope": scope, "state": state, "next_url": next_url}
    login_resp = await auth_client.get(
        "/login", params=login_params, allow_redirects=False
    )
    assert login_resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    session_resp = await auth_client.get("/session", cookies=login_resp.cookies)
    assert session_resp.json() == {"state": state, "next_url": next_url}
    redirect_url = login_resp.headers["Location"]
    oauth_query = {
        "client_id": conf.CLIENT_ID,
        "redirect_uri": conf.REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
        "state": state,
        "show_dialog": "false",
    }
    expected_url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(oauth_query)}"
    assert expected_url == redirect_url
    # Check redirection back to us (conf.REDIRECT_URI) from mocked Spotify OAuth
    oauth_resp = await auth_client.get(redirect_url, allow_redirects=False)
    assert oauth_resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    redirect_url = oauth_resp.headers["Location"]
    redirect_query = {"code": code, "state": state}
    expected_url = f"{conf.REDIRECT_URI}?{urlencode(redirect_query)}"
    assert expected_url == redirect_url
    # Check /login-redirect logic after mocked Spotify OAuth redirects back to us
    redirect_resp = await auth_client.get(
        redirect_url, cookies=login_resp.cookies, allow_redirects=False
    )
    assert redirect_resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    session_resp = await auth_client.get("/session", cookies=redirect_resp.cookies)
    assert session_resp.json() == {"scope": scope, "user": user_id}
    redirect_url = redirect_resp.headers["Location"]
    assert redirect_url == next_url
    assert await Token.objects.filter(user_id=user_id, scope=scope).exists()
