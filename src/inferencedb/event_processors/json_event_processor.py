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
    def __init__(self,
                 logger_name: str,
                 app: faust.App, 
                 config: Dict[str, Any]):
        pass

    async def process_event(self, event) -> Inference:
        return Inference(
            id=event["id"],
            model_name=event["model_name"],
            model_version=event.get("model_version"),
            inputs=pd.DataFrame.from_records(event["inputs"]),
            outputs=pd.DataFrame.from_records(event["outputs"]),
            occurred_at=isoparse(event["occurred_at"]) if event.get("occurred_at") is not None else None,
        )
