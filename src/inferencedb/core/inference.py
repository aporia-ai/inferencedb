from dataclasses import dataclass
from typing import Optional

import pandas as pd

from inferencedb.utils.pandas_utils import serialize_dataframe, deserialize_dataframe

@dataclass
class Inference:
    id: Optional[str] = None
    inputs: Optional[pd.DataFrame] = None
    outputs: Optional[pd.DataFrame] = None

    def serialize(self):
        return {
            "id": self.id,
            "inputs": serialize_dataframe(self.inputs),
            "outputs": serialize_dataframe(self.outputs),
        }

    @staticmethod
    def deserialize(data: dict):
        return Inference(
            id=data.get("id"),
            inputs=deserialize_dataframe(data.get("inputs")),
            outputs=deserialize_dataframe(data.get("outputs")),
        )
