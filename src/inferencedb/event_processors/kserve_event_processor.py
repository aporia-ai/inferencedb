from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

import faust

from inferencedb.registry.decorators import event_processor
from inferencedb.event_processors.inference import Inference
from .event_processor import EventProcessor


INFERENCE_REQUEST_TYPE = "org.kubeflow.serving.inference.request"
INFERENCE_RESPONSE_TYPE = "org.kubeflow.serving.inference.response"


@event_processor("kserve")
class KServeEventProcessor(EventProcessor):
    def __init__(self,
                 app: faust.App, 
                 config: Dict[str, Any]):
        # TODO: Validate config
        self._table = app.Table(
            # TODO: Need different name
            name="kserve-event-processor-state-4", 
            partitions=config["partitions"])

    async def process_event(self, event) -> Inference:
        # TODO: Figure out a standard return value for this function (Inference)
        # Basic validations on the event version.
        event_id = event.headers.get("ce_id", "").decode("utf-8")
        if not event_id:
            return

        if event.value is None:
            return
        
        # Add data to event, depending on the event type.
        event_type = event.headers.get("ce_type", "").decode("utf-8")
        if event_type == INFERENCE_REQUEST_TYPE:
            # Quick heuristic to make sure this isn't a metadata request
            if not all([True for item in event.value["inputs"] if "data" in item]):
                return

            inference = Inference(**self._table.get(event_id, {}))
            inference.inputs = {
                item["name"]: item["data"]
                for item in event.value["inputs"]
            }
        elif event_type == INFERENCE_RESPONSE_TYPE:
            # Quick heuristic to make sure this isn't a metadata request
            if not all([True for item in event.value["outputs"] if "data" in item]):
                return

            if "id" not in event.value:
                return
            
            inference = Inference(**self._table.get(event_id, {}))
            inference.id = event.value["id"]
            inference.outputs = {
                item["name"]: item["data"]
                for item in event.value["outputs"]
            }
        else:
            return
            
        # Merge events.
        self._table[event_id] = dict(inference)

        # Do we have all we need (request + response)?
        if inference.inputs is not None and inference.outputs is not None:
            self._table.pop(event_id)
            return inference
