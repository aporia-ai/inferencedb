from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

import faust

from inferencedb.event_processors.inference import Inference


class EventProcessor(ABC):
    """Abstract base class for EventProcessor objects."""

    @abstractmethod
    async def process_event(self, event) -> Inference:
        ...
