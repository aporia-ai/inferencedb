from dataclasses import dataclass
from typing import List, Optional

import numpy as np


@dataclass
class Inference:
    id: Optional[str] = None

    # For inputs and outputs, we always assume the first dimension is the
    # number of datapoints
    inputs: Optional[np.ndarray] = None
    outputs: Optional[np.ndarray] = None

    # These are only relevant for tabular data
    inputs_columns: Optional[List[str]] = None
    outputs_columns: Optional[List[str]] = None

    @staticmethod
    def from_dict(data: dict):
        return Inference(
            id=data.get("id"),
            inputs=np.array(data["inputs"]) if data.get("inputs") is not None else None,
            outputs=np.array(data["outputs"]) if data.get("outputs") is not None else None,
            inputs_columns=data.get("inputs_columns"),
            outputs_columns=data.get("outputs_columns"),
        )



# import orjson
# print(orjson.dumps(Inference(inputs=np.array([1,2,3])), option=orjson.OPT_SERIALIZE_NUMPY|orjson.OPT_SERIALIZE_DATACLASS))