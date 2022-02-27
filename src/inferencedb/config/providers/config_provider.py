from abc import ABC, abstractmethod
from asyncio import Event


class ConfigProvider(ABC):
    """Abstract base class for config providers."""

    def __init__(self):
        """Initializes a ConfigProvider."""
        self._config = {}
        self._update_event = Event()

    def get_config(self) -> dict:
        """Returns the current configuration."""
        return self._config

    def update_config(self, new_config: dict):
        """Updates the current configuration.

        Args:
            new_config: New config
        """
        if new_config != self._config:
            self._config = new_config
            self._update_event.set()

    async def wait_for_update(self):
        """Waits for the current configuration to be updated."""
        await self._update_event.wait()
        self._update_event.clear()

    @abstractmethod
    async def run(self):
        """Runs the config provider."""
        ...
