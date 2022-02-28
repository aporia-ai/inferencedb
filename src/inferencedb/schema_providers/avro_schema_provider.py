from typing import Any, AsyncIterator, Dict, List

import pandas as pd
from pandavro import schema_infer
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer
from schema_registry.client.schema import AvroSchema

from inferencedb.registry.decorators import schema_provider
from inferencedb.schema_providers.schema_provider import SchemaProvider
from inferencedb.core.inference import Inference

AVRO_NAMESPACE = "com.aporia.inferencedb.v1alpha1"


@schema_provider("avro")
class AvroSchemaProvider(SchemaProvider):
    def __init__(self,
        logger_name: str,
        schema_registry: AsyncSchemaRegistryClient,
        subject: str,
        config: Dict[str, Any]
    ):
        self._logger_name = logger_name
        self._schema_registry = schema_registry
        self._subject = subject
        self._config = config
        self._serializer = AsyncAvroMessageSerializer(self._schema_registry)
        self._schema: AvroSchema = None
        self._is_columnar = config.get("columnar", True)

        self._input_column_names = None
        self._output_column_names = None

        if "columnNames" in config:
            self._input_column_names = config["columnNames"].get("inputs")
            self._output_column_names = config["columnNames"].get("outputs")

    async def fetch(self):
        # If a schema is already registered in the Schema Registry, use it.
        response = await self._schema_registry.get_schema(self._subject)
        if response is None:
            return

        self._schema = response.schema

    async def serialize(self, inference: Inference) -> AsyncIterator[bytes]:
        # Override input columns
        if self._input_column_names is not None:
            inference.inputs.columns = self._input_column_names
        elif (
            isinstance(inference.inputs.columns, pd.RangeIndex) or
            inference.inputs.columns == [str(i) for i in range(len(inference.inputs.columns))]
        ):
            inference.inputs.columns = [f"X{i}" for i in range(len(inference.inputs.columns))]
        
        # Override output columns
        if self._output_column_names is not None:
            inference.outputs.columns = self._output_column_names
        elif (
            isinstance(inference.outputs.columns, pd.RangeIndex) or
            inference.outputs.columns == [str(i) for i in range(len(inference.outputs.columns))]
        ):
            inference.outputs.columns = [f"Y{i}" for i in range(len(inference.outputs.columns))]
        
        if self._schema is None:
            await self._generate_schema_from_inference(inference)

        # TODO: Make sure the shape of every input & output is the same
        for i, ((_, inputs), (_, outputs)) in enumerate(zip(inference.inputs.iterrows(), inference.outputs.iterrows())):            
            yield await self._serializer.encode_record_with_schema(
                subject=self._logger_name,
                schema=self._schema,
                record={
                    "id": f"{inference.id}_{i}",
                    **inputs.to_dict(),
                    **outputs.to_dict()
                },
            )

    async def _generate_schema_from_inference(self, inference: Inference):
        self._schema = AvroSchema({
            "type": "record",
            "namespace": AVRO_NAMESPACE,
            "name": self._logger_name.replace("-", "_"),
            "fields": [
                {"name": "id", "type": "string"},
                *schema_infer(inference.inputs)["fields"],
                *schema_infer(inference.outputs)["fields"],
            ],
        })

        self._input_column_names = inference.inputs.columns
        self._output_column_names = inference.outputs.columns

        await self._schema_registry.register(self._subject, self._schema)
