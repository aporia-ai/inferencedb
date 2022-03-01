from abc import ABC, abstractmethod

import pandas as pd

from inferencedb.core.inference import Inference


class EventProcessor(ABC):
    """Abstract base class for EventProcessor objects."""

    @abstractmethod
    async def process_event(self, event) -> Inference:
        ...
