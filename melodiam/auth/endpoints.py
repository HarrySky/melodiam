from typing import List, Optional, Union

from fastapi import Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from httpx import AsyncClient
from starlette import status
from tekore import (  # type: ignore[import]
    AsyncSender,
    ClientError,
    Credentials,
    ServerError,
    Spotify,
    Token as TekoreToken,
)
from tekore.model import PrivateUser  # type: ignore[import]

from melodiam import conf
from melodiam.auth.models import Token
from melodiam.resources import database
from melodiam.util.loghelper import init_logger
from melodiam.util.webhelper import envelope

_logger = init_logger()
_credentials: Credentials = None  # type: ignore[assignment]
_api: Spotify = None  # type: ignore[assignment]


def _check_initialized() -> None:
    if _credentials is None or _api is None:
        raise UnboundLocalError("API not ready, run startup() method!")


async def startup() -> None:
    global _credentials, _api
    _credentials = Credentials(
        conf.CLIENT_ID,
        conf.CLIENT_SECRET,
        conf.REDIRECT_URI,
        sender=AsyncSender(AsyncClient(http2=True, timeout=conf.SPOTIFY_API_TIMEOUT)),
        asynchronous=True,
    )
    _api = Spotify(
        sender=AsyncSender(AsyncClient(http2=True, timeout=conf.SPOTIFY_API_TIMEOUT)),
        asynchronous=True,
    )
    await database.connect()
    _logger.info("melodiam-auth started")


async def shutdown() -> None:
    await database.disconnect()
    _logger.info("melodiam-auth exited")


async def login(
    request: Request,
    state: str = Query(..., title="State for this login attempt"),  # noqa: B008
    next_url: str = Query("/", title="Where to redirect after success"),  # noqa: B008
    scope: Optional[List[str]] = Query(  # noqa: B008
        None, title="Scopes to request from Spotify"
    ),
) -> RedirectResponse:
    _check_initialized()
    request.session["state"] = state
    request.session["next_url"] = next_url
    oauth_url = _credentials.user_authorisation_url(scope, state)
    return RedirectResponse(oauth_url)


async def login_redirect(
    request: Request,
    code: str = Query(  # noqa: B008
        ..., title="Secret code for getting Spotify Web API token"
    ),
    state: str = Query(..., title="State for this login attempt"),  # noqa: B008
) -> Union[RedirectResponse, JSONResponse]:
    _check_initialized()
    if request.session.get("state") != state:
        return envelope(
            description="State in session and request don't match!",
            status=status.HTTP_409_CONFLICT,
        )

    try:
        token: TekoreToken = await _credentials.request_user_token(code)
    except (ClientError, ServerError):
        _logger.exception("Error during request for user token:")
        return envelope(
            description="Cannot obtain token with provided code!",
            status=status.HTTP_401_UNAUTHORIZED,
        )

    with _api.token_as(token) as api:
        user: PrivateUser = await api.current_user()
        request.session["state"] = state
        request.session["user"] = user.id

    # TODO: REFACTOR. Wrap this in try-catch block (INSERT can fail)
    await Token.upsert(user.id, token)
    next_url = request.session.get("next_url", "/")
    return RedirectResponse(next_url)
