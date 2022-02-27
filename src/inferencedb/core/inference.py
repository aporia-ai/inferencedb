from dataclasses import dataclass
from typing import Any, Optional, cast

import pandas as pd
import quickle

from inferencedb.utils.pandas_utils import deserialize_dataframe, serialize_dataframe

_quickle_encoder = quickle.Encoder()
_quickle_decoder = quickle.Decoder()


@dataclass
class Inference:
    id: Optional[str] = None
    inputs: Optional[pd.DataFrame] = None
    outputs: Optional[pd.DataFrame] = None

    def serialize(self):
        return _quickle_encoder.dumps({
            "id": self.id,
            "inputs": serialize_dataframe(self.inputs),
            "outputs": serialize_dataframe(self.outputs),
        })

    @staticmethod
    def deserialize(buf: bytes):
        if buf is None:
            return Inference()

        data = _quickle_decoder.loads(buf)
        return Inference(
            id=data.get("id"),
            inputs=deserialize_dataframe(data["inputs"]),
            outputs=deserialize_dataframe(data["outputs"]),
        )
