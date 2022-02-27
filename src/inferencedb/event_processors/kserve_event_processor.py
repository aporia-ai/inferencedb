from typing import Any, Dict

import faust
from inferencedb.core.inference import Inference

from inferencedb.registry.decorators import event_processor
from inferencedb.utils.kserve_utils import parse_kserve_request, parse_kserve_response
from .event_processor import EventProcessor


INFERENCE_REQUEST_TYPE = "org.kubeflow.serving.inference.request"
INFERENCE_RESPONSE_TYPE = "org.kubeflow.serving.inference.response"


@event_processor("kserve")
class KServeEventProcessor(EventProcessor):
    def __init__(self,
                 logger_name: str,
                 app: faust.App, 
                 config: Dict[str, Any]):
        # TODO: Validate config
        self._table = app.Table(
            name=f"kserve-event-processor-state-{logger_name}",
            partitions=config.get("partitions", None),
            value_type=bytes)
        
    async def process_event(self, event) -> Inference:
        # Basic validations on the event version.
        event_id = event.headers.get("ce_id", "").decode("utf-8")
        if not event_id:
            return

        if event.value is None:
            return
        
        # Add data to event, depending on the event type.
        event_type = event.headers.get("ce_type", "").decode("utf-8")
        
        inference = Inference.deserialize(self._table.get(event_id, None))
        
        if event_type == INFERENCE_REQUEST_TYPE:
            inference.inputs = parse_kserve_request(event.value)
        elif event_type == INFERENCE_RESPONSE_TYPE:
            if "id" not in event.value:
                return

            inference.id = event.value["id"]
            inference.outputs = parse_kserve_response(event.value)
        else:
            return
            
        # Merge events.
        self._table[event_id] = inference.serialize()

        # Do we have all we need (request + response)?
        if (
            inference.id is not None and
            inference.inputs is not None and
            inference.outputs is not None
        ):
            self._table.pop(event_id)
            return inference
