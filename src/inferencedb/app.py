import asyncio
from inferencedb.config.factory import create_config_provider, generate_config_from_dict
from inferencedb.config.providers.kubernetes_config_provider import KubernetesConfigProvider
from inferencedb.core.inference_logger import InferenceLogger
from inferencedb.core.logging_utils import generate_logging_config, init_logging
import faust
import json
import os
import ssl
import logging

import aiohttp

from inferencedb.utils.asyncio_utils import cancling_background_task
from .settings import Settings
from schema_registry.client import AsyncSchemaRegistryClient


settings = Settings()

# Initialize logging
init_logging(log_level=settings.log_level)
logging.info("Worker started.")


# Load TLS certificates if necessary
ssl_context = None
if os.path.isdir("/etc/kafka-tls"):
    ssl_context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH, 
        cafile="/etc/kafka-tls/ca.crt",
    )
    ssl_context.load_cert_chain("/etc/kafka-tls/user.crt", keyfile="/etc/kafka-tls/user.key")


# Create Faust app
app = faust.App(
    id="inferencedb", 
    broker=settings.kafka_broker, 
    store="rocksdb://",
    autodiscover=True,
    origin="inferencedb",
    broker_credentials=ssl_context,

    # Faust's internal logging level is INFO because DEBUG is just unreadable.
    # FUTURE: Maybe add here support for WARNING, ERROR, CRITICAL.
    logging_config=generate_logging_config(log_level="INFO"),
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
        metadata = inference_logger['metadata']

        # FUTURE: These should be in a separate utility function, which we can reuse in InferenceLogger and Destination.
        logger_name = f"{metadata['namespace']}-{metadata['name']}"
        connector_name = f"inferencedb-{logger_name}"
        
        for _ in range(10):
            async with aiohttp.ClientSession(
                base_url=settings.kafka_connect_url,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as session:
                async with session.delete(url=f"/connectors/{connector_name}") as response:
                    if response.status == 409:
                        # Kafka connect rebalance
                        await asyncio.sleep(3)
                        continue
                    elif response.status not in (204, 404):
                        raise RuntimeError(f"Failed to delete Kafka Connector: {connector_name}")

        raise RuntimeError(f"Could not delete connector because of Kafka Connect rebalance.")

    await config_provider.manage_finalizers(remove_kafka_connector)


# Create all inference loggers.
for item in config.inference_loggers:
    inference_logger = InferenceLogger(app, schema_registry, item)
    inference_logger.register()
