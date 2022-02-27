import faust
from inferencedb.config.component import ComponentConfig

from schema_registry.client import AsyncSchemaRegistryClient

from inferencedb.config.config import InferenceLoggerConfig
from inferencedb.event_processors.factory import create_event_processor
from inferencedb.event_processors.kserve_event_processor import KServeEventProcessor
from inferencedb.schema_providers.factory import create_schema_provider
from inferencedb.schema_providers.avro_schema_provider import AvroSchemaProvider

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

        # TODO: Comment
        self._target_topic = app.topic(config.name)

        # TODO: Comment
        schema_provider_config = config.schema_provider
        if schema_provider_config is None:
            schema_provider_config = DEFAULT_SCHEMA_PROVIDER_CONFIG
            
        self._schema_provider = create_schema_provider(schema_provider_config.type, {
            "logger_name": config.name,
            "subject": f"{self._target_topic.get_topic_name()}-value",
            "schema_registry": self._schema_registry,
            "config": schema_provider_config.config,
        })

        # TODO: Comment
        self._source_topic = app.topic(self._config.topic)
        self._event_processor = create_event_processor(config.event_processor.type, {
            "logger_name": config.name,
            "app": app, 
            "config": config.event_processor.config,
        })
        

        # TODO: Destination
        # TODO: Delete this when the CRD is deleted - can prefix with "__inferencedb" and GET /connectors to see all existing
        # TODO: Add timestamp field
        # POST http://localhost:8083/connectors
        # {
        # 	"name": "my-model-sink",
        # 	"config": {
        # 		"connector.class": "io.confluent.connect.s3.S3SinkConnector",
        # 		"storage.class": "io.confluent.connect.s3.storage.S3Storage",
        # 		"s3.region": "us-east-2",
        # 		"s3.bucket.name": "aporia-data",
        # 		"topics.dir": "my-model-test-2",
        # 		"flush.size": "2",
        # 		"rotate.schedule.interval.ms": "20000",
        # 		"auto.register.schemas": "false",
        # 		"tasks.max": "1",
        # 		"s3.part.size": "5242880",
        # 		"timezone": "UTC",
        # 		"parquet.codec": "snappy",
        # 		"topics": "my_avro_topic",
        # 		"schema.registry.url": "http://kafka-cp-schema-registry:8081",
        # 		"s3.credentials.provider.class": "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
        # 		"format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
        # 		"value.converter": "io.confluent.connect.avro.AvroConverter",
        # 		"key.converter": "org.apache.kafka.connect.storage.StringConverter",
        # 		"value.converter.schema.registry.url": "http://kafka-cp-schema-registry:8081"
        # 	}
        # }

    def register(self):
        async def agent(stream):
            await self._schema_provider.fetch()

            # Process every inference event
            async for event in stream.events():
                inference = await self._event_processor.process_event(event)
                if inference is None:
                    continue

                # Serialize each inference
                async for item in self._schema_provider.serialize(inference):
                    yield item

        self._app.agent(self._source_topic, sink=[self._target_topic])(agent)
