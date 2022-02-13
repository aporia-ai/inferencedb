from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

import faust
import aiohttp

from inferencedb.registry.decorators import schema_provider
from .schema_provider import SchemaProvider
from schema_registry.client.schema import AvroSchema

KSERVE_DATATYPE_TO_AVRO = {
    "BOOL": "boolean",
    "INT32": "int",
    "INT64": "long",
    "FP32": "float",
    "FP64": "double",
    "BYTES": "string",  # TODO: content-type = str --> string, otherwise bytes
}


@schema_provider("kserve")
class KServeSchemaProvider(SchemaProvider):
    def __init__(self, config: Dict[str, Any]):
        # TODO: Validate config
        self._config = config

    async def get_schema(self) -> AvroSchema:
        model_name = self._config["modelName"]
        protocol = self._config["protocol"]
        namespace = self._config["namespace"]
        # TODO: Version

        # TODO: Is it more right to query the K8s InferenceService and get status.address.url (contains /infer though)
        url = f'http://{model_name}.{namespace}.svc.cluster.local/{protocol}/models/{model_name}'

        # TODO: Consider caching aiohttp session 
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                metadata = await response.json()

        # Convert to Avro
        return AvroSchema({
            "type": "record",
            "namespace": "com.aporia.inferencedb",
            "name": "MyModel", # TODO
            "fields": [
                # Convert all inputs to Avro fields
                *[{"name": field["name"].replace(".", "_"), "type": KSERVE_DATATYPE_TO_AVRO[field["datatype"]]}
                  for field in metadata["inputs"]],

                # Convert all outputs to Avro fields
                *[{"name": field["name"].replace(".", "_"), "type": KSERVE_DATATYPE_TO_AVRO[field["datatype"]]}
                  for field in metadata["outputs"]]
            ],
        })
    