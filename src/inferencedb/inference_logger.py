import faust
from inferencedb.config.config import InferenceLoggerConfig
from inferencedb.event_processors.factory import create_event_processor
from inferencedb.event_processors.kserve_event_processor import KServeEventProcessor
from inferencedb.schema_providers.factory import create_schema_provider
from inferencedb.schema_providers.kserve_schema_provider import KServeSchemaProvider
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer


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
        self._avro_message_serializer = AsyncAvroMessageSerializer(self._schema_registry)

        # TODO: Comment
        self._schema_provider = create_schema_provider(config.schema_provider.type, {
            "config": config.schema_provider.config,
        })

        # TODO: Comment
        self._source_topic = app.topic(self._config.topic)
        self._event_processor = create_event_processor(config.event_processor.type, {
            "app": app, 
            "config": config.event_processor.config,
        })
        
        # TODO: Comment
        self._target_topic = app.topic(f"inferencedb-{config.name}-avro")


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
            # Register schema
            schema = await self._schema_provider.get_schema()
            await self._schema_registry.register(
                f"{self._target_topic.get_topic_name()}-value", schema)

            # Process every inference event
            async for event in stream.events():
                inference = await self._event_processor.process_event(event)
                if inference is None:
                    continue

                # Convert inference event to Avro
                # TODO: Make sure the shape of every input & output is the same
                for i in range(len(next(iter(inference.inputs.values())))):
                    avro_inference = await self._avro_message_serializer.encode_record_with_schema(
                        subject="my-model",  # TODO
                        schema=schema,
                        record={
                            **{key.replace(".", "_"): value[i] for key, value in inference.inputs.items()},
                            **{key.replace(".", "_"): value[i] for key, value in inference.outputs.items()},
                        },
                    )

                    yield avro_inference

        self._app.agent(self._source_topic, sink=[self._target_topic])(agent)
