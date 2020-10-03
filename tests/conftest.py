from asyncio import get_event_loop_policy
from logging import getLogger

import pytest


def no_problems_logged(capfd) -> bool:
    stderr = capfd
    if not isinstance(capfd, str):
        stderr = capfd.readouterr().err

    return all(x not in stderr for x in ("CRITICAL", "ERROR", "WARNING"))


@pytest.fixture(autouse=True)
def clear_logger():
    """Clear handlers to avoid errors when using logger in tests."""
    logger = getLogger("melodiam")
    handlers = getattr(logger, "handlers", [])
    for handler in handlers:
        logger.removeHandler(handler)


@pytest.yield_fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case to avoid errors.
    """
    loop = get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
