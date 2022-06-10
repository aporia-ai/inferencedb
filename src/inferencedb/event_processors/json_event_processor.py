from typing import Any, Dict
import pandas as pd
from datetime import datetime

import faust
from dateutil.parser import isoparse

from inferencedb.core.inference import Inference
from inferencedb.registry.decorators import event_processor
from .event_processor import EventProcessor


@event_processor("json")
class JSONEventProcessor(EventProcessor):
    def __init__(self, logger_name: str, app: faust.App, config: Dict[str, Any]):
        pass

    async def process_event(self, event) -> Inference:
        return Inference(
            id=event.get("id"),
            model_name=event.get("model_name"),
            model_version=event.get("model_version"),
            inputs=pd.DataFrame.from_records(event["inputs"]) if event.get("inputs") is not None else None,
            outputs=pd.DataFrame.from_records(event["outputs"]) if event.get("outputs") is not None else None,
            occurred_at=isoparse(event["occurred_at"]) if event.get("occurred_at") is not None else datetime.now(),
        )
