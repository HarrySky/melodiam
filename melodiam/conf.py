import sys
from os import R_OK, access, environ, path

from starlette.config import Config

_config_file = environ.get("MELODIAM_CONFIG", "tests/test.env")
if "--config" in sys.argv:
    _config_file = sys.argv[sys.argv.index("--config") + 1]

if not path.exists(_config_file) or not access(_config_file, R_OK):
    raise IOError(f"Config file ({_config_file}) does not exist or not readable")

_config = Config(env_file=_config_file)
DEBUG: bool = _config.get("DEBUG", bool, default=True)
# Secret key for session encryption
SESSION_SECRET: str = _config.get("SESSION_SECRET", str, default="change-me")
# Paths to use for auth API
LOGIN_PATH: str = _config.get("LOGIN_PATH", str, default="/login")
LOGIN_REDIRECT_PATH: str = _config.get(
    "LOGIN_REDIRECT_PATH", str, default="/login-redirect"
)
# Credentials required for Spotify Web API auth
CLIENT_ID: str = _config.get("CLIENT_ID", str)
CLIENT_SECRET: str = _config.get("CLIENT_SECRET", str)
REDIRECT_URI: str = _config.get("REDIRECT_URI", str)
# Timeout for Spotify Web API requests
SPOTIFY_API_TIMEOUT: int = _config.get("SPOTIFY_API_TIMEOUT", int, default=1)
# URL used for PostgreSQL connection
DATABASE_URL: str = _config.get(
    "DATABASE_URL",
    str,
    default="postgresql:///melodiam?user=melodiam&host=localhost&port=5432",
)
