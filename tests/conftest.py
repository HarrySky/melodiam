from asyncio import AbstractEventLoop, get_event_loop_policy
from logging import getLogger
from typing import Any, AsyncGenerator, Generator

import pytest
from httpx import AsyncClient


def no_problems_logged(capfd: Any) -> bool:
    stderr = capfd
    if not isinstance(capfd, str):
        stderr = capfd.readouterr().err

    return all(x not in stderr for x in ("CRITICAL", "ERROR", "WARNING"))


@pytest.fixture(autouse=True)
def clear_logger() -> None:
    """Clear handlers to avoid errors when using logger in tests."""
    logger = getLogger("melodiam")
    handlers = getattr(logger, "handlers", [])
    for handler in handlers:
        logger.removeHandler(handler)


@pytest.fixture(scope="session")
async def auth_client() -> AsyncGenerator[AsyncClient, None]:
    from melodiam.auth import api, endpoints

    await endpoints.startup()
    # Patch sender
    endpoints._credentials.sender.client = endpoints._api.sender.client = AsyncClient(
        app=api, base_url="https://accounts.spotify.com"
    )
    async with AsyncClient(app=api, base_url="http://localhost:7455") as client:
        yield client

    await endpoints.shutdown()


@pytest.yield_fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for each test case to avoid errors.
    """
    loop = get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
