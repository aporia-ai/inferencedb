from abc import ABC, abstractmethod
from typing import AsyncIterator

from inferencedb.core.inference import Inference


class SchemaProvider(ABC):
    """Abstract base class for SchemaProvider objects."""

    @abstractmethod
    async def fetch(self):
        ...

    @abstractmethod
    async def serialize(self, inference: Inference) -> AsyncIterator[bytes]:
        ...
