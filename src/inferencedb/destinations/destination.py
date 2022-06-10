from abc import ABC, abstractmethod


class Destination(ABC):
    """Abstract base class for Destination objects."""

    @abstractmethod
    async def create_connector(self):
        ...
