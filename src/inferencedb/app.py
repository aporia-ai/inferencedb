from inferencedb.config.config import InferenceLoggerConfig
from inferencedb.config.factory import create_config_provider, generate_config_from_dict
from inferencedb.config.providers.kubernetes_config_provider import KubernetesConfigProvider
from inferencedb.inference_logger import InferenceLogger
import faust
import asyncio

from inferencedb.utils import cancling_background_task
from .settings import Settings
from schema_registry.client import AsyncSchemaRegistryClient


settings = Settings()


async def create_app():
    config_provider = create_config_provider(
        name=settings.config_provider,
        params=settings.config_provider_args,
    )

    with cancling_background_task(config_provider.run()):
        # while True:  # TODO
        # Wait for a configuration update.
        await config_provider.wait_for_update()

        # We have a new config! Parse it.
        config = generate_config_from_dict(config_provider.get_config())

        # Create a new Faust app.
        app = faust.App(
            id="inferencedb", 
            broker=settings.kafka_broker, 
            store="rocksdb://",
            autodiscover=True,
            origin="inferencedb"
        )

        # Connect to schema registry.
        schema_registry = AsyncSchemaRegistryClient(url=settings.kafka_schema_registry_url)

        worker = faust.Worker(app, loglevel="INFO", loop=asyncio.get_event_loop())

        # Create an agent for each InferenceLogger.
        for inference_logger_config in config.inference_loggers:
            inference_logger = InferenceLogger(app, schema_registry, inference_logger_config)
            inference_logger.start()

        await worker.start() 
        # await worker.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_app())
