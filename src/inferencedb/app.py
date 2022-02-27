from inferencedb.config.factory import create_config_provider, generate_config_from_dict
from inferencedb.config.providers.kubernetes_config_provider import KubernetesConfigProvider
from inferencedb.core.inference_logger import InferenceLogger
import faust
import asyncio

from inferencedb.utils.asyncio_utils import cancling_background_task
from .settings import Settings
from schema_registry.client import AsyncSchemaRegistryClient


settings = Settings()


async def create_app():
    config_provider = create_config_provider(
        name=settings.config_provider,
        params=settings.config_provider_args,
    )

    worker = None

    with cancling_background_task(config_provider.run()):     
        # Connect to schema registry.
        schema_registry = AsyncSchemaRegistryClient(url=settings.kafka_schema_registry_url)

        # Wait for the first configuration.
        await config_provider.wait_for_update()

        worker = None

        while True:
            # Parse config.
            config = generate_config_from_dict(config_provider.get_config())

            # Create a new Faust app.
            app = faust.App(
                id="inferencedb", 
                broker=settings.kafka_broker, 
                store="rocksdb://",
                autodiscover=True,
                origin="inferencedb"
            )
            
            # Create a Faust worker with an agent for each InferenceLogger.
            worker = faust.Worker(app, loglevel="INFO", loop=asyncio.get_event_loop())
            for inference_logger_config in config.inference_loggers:
                inference_logger = InferenceLogger(app, schema_registry, inference_logger_config)
                inference_logger.register()

            # Wait for a configuration update.
            worker_task = asyncio.create_task(worker.start())
            update_task = asyncio.create_task(config_provider.wait_for_update())

            done, pending = await asyncio.wait(
                [worker_task, update_task], return_when=asyncio.FIRST_COMPLETED
            )

            if worker_task in pending:
                await worker.stop()
                await app.stop()

                worker_task.cancel()
            
            if update_task in pending:
                update_task.cancel()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_app())
