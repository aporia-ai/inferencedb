import asyncio
from contextlib import contextmanager
from typing import Coroutine, Dict, Generator, Optional, Union


@contextmanager
def cancling_background_task(coro: Coroutine) -> Generator[asyncio.Task, None, None]:
    """Schedules a coroutine to run in the background, canceling it when the context manager exits.

    Args:
        coro: Coroutine to schedule

    Yields:
        The scheduled task object.
    """
    task = asyncio.create_task(coro)
    yield task
    task.cancel()

