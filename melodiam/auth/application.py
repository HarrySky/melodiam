from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from melodiam import __version__, conf
from melodiam.auth import endpoints

api = FastAPI(
    debug=conf.DEBUG,
    title="Melodiam Auth API",
    version=__version__,
    root_path="/api",
    on_startup=[endpoints.on_startup],
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)
api.add_middleware(
    SessionMiddleware,
    secret_key=conf.SESSION_SECRET,
    same_site="lax",
    https_only=not conf.DEBUG,
)
api.add_api_route(
    conf.LOGIN_PATH,
    endpoints.login,
    methods=["GET"],
)
api.add_api_route(
    conf.LOGIN_REDIRECT_PATH,
    endpoints.login_redirect,
    methods=["GET"],
)
