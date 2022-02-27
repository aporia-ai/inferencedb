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

        if self._is_columnar:
            # Extract input column names from the schema if the user didn't specify any.
            if self._input_column_names is not None:
                self._input_column_names = self._extract_column_names("inputs")

            # Extract output column names from the schema if the user didn't specify any.
            if self._output_column_names is not None:
                self._output_column_names = self._extract_column_names("outputs")

    async def serialize(self, inference: Inference) -> AsyncIterator[bytes]:
        if self._schema is None:
            self._generate_schema_from_inference()

        # TODO: Make sure the shape of every input & output is the same

        for (_, inputs), (_, outputs) in zip(inference.inputs.iterrows(), inference.outputs.iterrows()):
            yield await self._serializer.encode_record_with_schema(
                subject=self._logger_name,
                schema=self._schema,
                record={
                    # "id": inference.id, # TODO
                    "inputs": inputs.to_dict(),
                    "outputs": outputs.to_dict()
                },
            )

    async def _generate_schema_from_inference(self, inference: Inference):
        # Use input column names from config if specified
        if self._input_column_names is not None:
            inference.inputs.columns = self._input_column_names

        # Use output column names from config if specified
        if self._input_column_names is not None:
            inference.inputs.columns = self._input_column_names

        # Build schema
        self._schema = AvroSchema({
            "type": "record",
            "namespace": AVRO_NAMESPACE,
            "name": self._logger_name,
            "fields": [
                {
                    "name": "inputs",
                    "type": schema_infer(inference.inputs)
                },
                {
                    "name": "outputs",
                    "type": schema_infer(inference.outputs)
                },
            ],
        })

        await self._schema_registry.register(self._subject, self._schema)
        
    def _extract_column_names(self, field_name: str) -> List[str]:
        fields = next(
            field["type"]["fields"] 
            for field in self._schema.schema["fields"]
            if field["name"] == field_name
        )

        return [field["name"] for field in fields]
