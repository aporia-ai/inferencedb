from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from schema_registry.client.schema import AvroSchema


class SchemaProvider(ABC):
    """Abstract base class for SchemaProvider objects."""

    @abstractmethod
    async def get_schema(self) -> AvroSchema:
        ...
