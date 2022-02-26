from asyncio import protocols
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import faust
import numpy as np
import orjson

from inferencedb.registry.decorators import event_processor
from .event_processor import EventProcessor, Inference


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
            name="kserve-event-processor-state_1",
            partitions=config.get("partitions", None))

    async def process_event(self, event) -> Inference:
        # Basic validations on the event version.
        event_id = event.headers.get("ce_id", "").decode("utf-8")
        if not event_id:
            return

        if event.value is None:
            return
        
        # Add data to event, depending on the event type.
        event_type = event.headers.get("ce_type", "").decode("utf-8")
        
        inference = Inference.from_dict(self._table.get(event_id, {}))
        if event_type == INFERENCE_REQUEST_TYPE:
            inference.inputs, inference.inputs_columns = self._parse_kserve_fragment(
                event.value,
                v1_key="instances",
                v2_key="inputs",
            )
        elif event_type == INFERENCE_RESPONSE_TYPE:
            if "id" not in event.value:
                return

            inference.id = event.value["id"]
            inference.outputs, inference.outputs_columns = self._parse_kserve_fragment(
                event.value,
                v1_key="predictions",
                v2_key="outputs",
            )
        else:
            return
            
        # Merge events.
        self._table[event_id] = orjson.dumps(inference, 
            option=orjson.OPT_SERIALIZE_NUMPY|orjson.OPT_SERIALIZE_DATACLASS)

        # Do we have all we need (request + response)?
        if inference.inputs is not None and inference.outputs is not None:
            self._table.pop(event_id)
            return inference

    def _parse_kserve_fragment(
        self,
        data: dict,
        v1_key: str = "instances",
        v2_key: str = "inputs"
    ) -> Tuple[np.ndarray, List[str]]:
        # KServe Protocol v1
        if v1_key in data:
            arr = np.array(data[v1_key])
            if len(arr.shape) == 1:
                arr = np.expand_dims(arr, axis=1)
                
            return (arr, None)

        # KServe Protocol v2
        elif v2_key in data:
            columns = data[v2_key]
            
            # Stack all columns.
            result = np.column_stack([column["data"] for column in columns])
            
            # Figure out if we can use column names from the request.
            column_names = None
            if len(columns) == result.shape[1]:
                column_names = [column["name"] for column in columns]

            return (result, column_names)

        else:
            raise ValueError(f"Invalid KServe request: no '{v1_key}' or '{v2_key}' fields")
