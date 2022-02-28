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
            name=f"kserve-event-processor-{logger_name}__3",
            value_type=bytes
        ).tumbling(10.0, expires=10.0)
        
    async def process_event(self, event) -> Inference:
        # Basic validations on the event version.
        event_id = faust.current_event().headers.get("ce_id", "").decode("utf-8")
        if not event_id:
            return

        if event is None:
            return
        
        # Add data to event, depending on the event type.
        event_type = faust.current_event().headers.get("ce_type", "").decode("utf-8")

        try:
            inference = Inference.deserialize(self._table[event_id].value())
        except KeyError:
            inference = Inference()
        
        if event_type == INFERENCE_REQUEST_TYPE:
            inference.inputs = parse_kserve_request(event)
        elif event_type == INFERENCE_RESPONSE_TYPE:
            if "id" not in event:
                return

            inference.id = event["id"]
            inference.model_name = event.get("model_name")
            inference.model_version = event.get("model_version")
            inference.outputs = parse_kserve_response(event)
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

    @staticmethod
    def get_group_key(event):
        return faust.current_event().headers.get("ce_id", "").decode("utf-8")
