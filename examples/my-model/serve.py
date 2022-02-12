from mlserver import MLModel
from mlserver.types import InferenceRequest, InferenceResponse, ResponseOutput, MetadataTensor
import lightgbm as lgb
import pandas as pd
import numpy as np
import joblib


flower_name_by_index = {0: 'Setosa', 1: 'Versicolor', 2: 'Virginica'}

class MyModelRuntime(MLModel):
    async def load(self):
        self._model = joblib.load("my-model.lgb")

        self.inputs = [
            MetadataTensor(name=column, datatype="FP32", shape=[])
            for column in self._model.feature_name()
        ]

        self.outputs = [
            MetadataTensor(name="proba", datatype="FP32", shape=[]),
            MetadataTensor(name="variety", datatype="BYTES", shape=[],
                           parameters={"content_type": "str"})
        ]

        self.ready = True
        return self.ready

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        # TODO: Make sure that the input column names are correct.
        
        X = pd.DataFrame.from_dict({
            item.name: item.data
            for item in payload.inputs
        })

        y = self._model.predict(X)

        return InferenceResponse(
            id=payload.id,
            model_name=self.name,
            model_version=self.version,
            outputs=[
                ResponseOutput(
                    name="proba",
                    data=np.max(y, axis=1).tolist(),
                    shape=[len(y)],
                    datatype="FP32"
                ),
                ResponseOutput(
                    name="variety",
                    data=[flower_name_by_index[pred] for pred in np.argmax(y, axis=1)],
                    shape=[len(y)],
                    datatype="BYTES", 
                    parameters={"content_type": "str"}
                )
            ],
        )

    
