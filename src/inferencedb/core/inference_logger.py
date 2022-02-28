import logging
import faust
from inferencedb.config.component import ComponentConfig

from schema_registry.client import AsyncSchemaRegistryClient

from inferencedb.config.config import InferenceLoggerConfig
from inferencedb.event_processors.factory import create_event_processor
from inferencedb.event_processors.kserve_event_processor import KServeEventProcessor
from inferencedb.schema_providers.factory import create_schema_provider
from inferencedb.schema_providers.avro_schema_provider import AvroSchemaProvider
from inferencedb.destinations.factory import create_destination
from inferencedb.destinations.confluent_s3_destination import ConfluentS3Destination

DEFAULT_SCHEMA_PROVIDER_CONFIG = ComponentConfig(type="avro", config={})


class InferenceLogger:
    def __init__(
        self, 
        app: faust.App, 
        schema_registry: AsyncSchemaRegistryClient,
        config: InferenceLoggerConfig
    ):
        self._app = app
        self._config = config
        self._schema_registry = schema_registry

        # Create the target topic
        self._target_topic = app.topic(config.name)

        # Create schema provider
        schema_provider_config = config.schema_provider
        if schema_provider_config is None:
            schema_provider_config = DEFAULT_SCHEMA_PROVIDER_CONFIG
            
        self._schema_provider = create_schema_provider(schema_provider_config.type, {
            "logger_name": config.name,
            "subject": f"{self._target_topic.get_topic_name()}-value",
            "schema_registry": self._schema_registry,
            "config": schema_provider_config.config,
        })

        # Create event processor
        self._source_topic = app.topic(self._config.topic)
        self._event_processor = create_event_processor(config.event_processor.type, {
            "logger_name": config.name,
            "app": app, 
            "config": config.event_processor.config,
        })
        
        # Create destination
        self._destination = create_destination(config.destination.type, {
            "logger_name": config.name,
            "topic": self._target_topic.get_topic_name(),
            "config": config.destination.config,
        })

    def register(self):
        async def agent(stream):
            # Create the Kafka connector
            await self._destination.create_connector()

            # Process every inference event
            async for event in stream.group_by(
                name=self._config.name,
                key=self._event_processor.get_group_key,
            ):
                inference = await self._event_processor.process_event(event)
                if inference is None:
                    continue

                # Apply filters.
                # FUTURE: Do this in a more generic way.
                filters = self._config.filters
                if filters is not None:
                    if filters.get("modelName") is not None and filters["modelName"] != inference.model_name:
                        continue

                    if filters.get("modelVersion") is not None and filters["modelVersion"] != inference.model_name:
                        continue

                # Serialize each inference
                async for item in self._schema_provider.serialize(inference):
                    yield item

        self._app.agent(
            name=self._config.name,
            channel=self._source_topic,
            sink=[self._target_topic]
        )(agent)
