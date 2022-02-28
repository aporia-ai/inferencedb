from inferencedb.config.factory import create_config_provider, generate_config_from_dict
from inferencedb.config.providers.kubernetes_config_provider import KubernetesConfigProvider
from inferencedb.core.inference_logger import InferenceLogger
import faust
import json
import os

from inferencedb.utils.asyncio_utils import cancling_background_task
from .settings import Settings
from schema_registry.client import AsyncSchemaRegistryClient


settings = Settings()

app = faust.App(
    id="inferencedb", 
    broker=settings.kafka_broker, 
    store="rocksdb://",
    autodiscover=True,
    origin="inferencedb"
)


config = generate_config_from_dict(json.loads(os.environ["CONFIG"]))

# Connect to schema registry.
schema_registry = AsyncSchemaRegistryClient(url=settings.kafka_schema_registry_url)


# Remove old InferenceLogger Kafka connectors.
@app.task(on_leader=True)
async def remove_old_inferenceloggers():
    config_provider = create_config_provider(
        name=settings.config_provider,
        params=settings.config_provider_args,
    )

    async def remove_kafka_connector(inference_logger: dict):
        print("REMOVING KAFKA CONNECTOR FOR RESOURCE", inference_logger)

    await config_provider.manage_finalizers(remove_kafka_connector)


# Create all inference loggers.
for item in config.inference_loggers:
    inference_logger = InferenceLogger(app, schema_registry, item)
    inference_logger.register()
