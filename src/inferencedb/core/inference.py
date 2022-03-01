from dataclasses import dataclass
from typing import Any, Dict, Optional, cast
from datetime import datetime

import pandas as pd
import quickle
from dateutil.parser import isoparse

from inferencedb.utils.pandas_utils import deserialize_dataframe, serialize_dataframe

_quickle_encoder = quickle.Encoder()
_quickle_decoder = quickle.Decoder()


@dataclass
class Inference:
    id: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    inputs: Optional[pd.DataFrame] = None
    outputs: Optional[pd.DataFrame] = None
    occurred_at: Optional[datetime] = None

    def serialize(self):
        return _quickle_encoder.dumps({
            "id": self.id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "inputs": serialize_dataframe(self.inputs),
            "outputs": serialize_dataframe(self.outputs),
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at is not None else None,
        })

    @staticmethod
    def deserialize(buf: bytes):
        if buf is None:
            return Inference()

        data = _quickle_decoder.loads(buf)
        return Inference(
            id=data.get("id"),
            model_name=data["model_name"],
            model_version=data["model_version"],
            inputs=deserialize_dataframe(data["inputs"]),
            outputs=deserialize_dataframe(data["outputs"]),
            occurred_at=isoparse(data["occurred_at"]) if data.get("occurred_at") is not None else None,
        )
