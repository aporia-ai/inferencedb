import faust
from inferencedb.config.config import InferenceLoggerConfig
from inferencedb.event_processors.factory import create_event_processor
from inferencedb.event_processors.kserve_event_processor import KServeEventProcessor
from inferencedb.schema_providers.factory import create_schema_provider
from inferencedb.schema_providers.kserve_schema_provider import KServeSchemaProvider
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer
from schema_registry.client.schema import AvroSchema


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
        if config.schema_provider is not None:
            self._schema_provider = create_schema_provider(config.schema_provider.type, {
                "config": config.schema_provider.config,
            })
        else:
            self._schema_provider = None

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
            schema = None
            schema_subject = f"{self._target_topic.get_topic_name()}-value"
            
            # If schema was provided, register it.
            if self._schema_provider is not None:
                schema = await self._schema_provider.get_schema()
                await self._schema_registry.register(schema_subject, schema)
            else:
                # Otherwise, try to fetch the latest schema from the Schema Registry.
                response = await self._schema_registry.get_schema(schema_subject)
                if response is not None:
                    schema = response.schema


            # Process every inference event
            async for event in stream.events():
                inference = await self._event_processor.process_event(event)
                if inference is None:
                    continue

                # Schema wasn't provided, so we need to register one from the first prediction.
                if inference.inputs_columns is None:
                    if schema is None:
                        inference.inputs_columns = [f"X{i}" for i in range(inference.inputs.shape[1])]
                    else:
                        inference.inputs_columns = [f["name"] for f in next(field["type"]["fields"] for field in schema.schema["fields"] if field["name"] == "inputs")]

                if inference.outputs_columns is None:
                    if schema is None:
                        inference.outputs_columns = [f"Y{i}" for i in range(inference.outputs.shape[1])]
                    else:
                        inference.outputs_columns = [f["name"] for f in next(field["type"]["fields"] for field in schema.schema["fields"] if field["name"] == "outputs")]

                if schema is None:
                    if len(inference.inputs.shape) != 2 or len(inference.outputs.shape) != 2:
                        raise RuntimeError("Inferencing schema from first prediction only supportrs tabular at the moment.")
                    
                    NUMPY_DATATYPE_TO_AVRO = {
                        "bool": "boolean",
                        "int32": "int",
                        "int64": "long",
                        "float32": "float",
                        "float64": "double",
                    }

                    schema = AvroSchema({
                        "type": "record",
                        "namespace": "com.aporia.inferencedb",
                        "name": "MyModel", # TODO
                        "fields": [
                            # Convert all inputs to Avro fields
                            {
                                "name": "inputs",
                                "type": {
                                    "type": "record",
                                    "name": "MyModelInputs",
                                    "fields": [{
                                        "name": column,
                                        "type": NUMPY_DATATYPE_TO_AVRO[inference.inputs.dtype.name]
                                    } for column in inference.inputs_columns],
                                },
                            },

                            # Convert all outputs to Avro fields
                            {
                                "name": "outputs",
                                "type": {
                                    "type": "record",
                                    "name": "MyModelOutputs",
                                    "fields": [{
                                        "name": column,
                                        "type": NUMPY_DATATYPE_TO_AVRO[inference.outputs.dtype.name]
                                    } for column in inference.outputs_columns],
                                },
                            },
                        ],
                    })

                    await self._schema_registry.register(schema_subject, schema)
                

                # Convert inference event to Avro
                # TODO: Make sure the shape of every input & output is the same
                for row in range(inference.inputs.shape[0]):
                    avro_inference = await self._avro_message_serializer.encode_record_with_schema(
                        subject="my-model",  # TODO
                        schema=schema,
                        record={
                            "inputs": {
                                inference.inputs_columns[column]: inference.inputs[row][column]
                                for column in range(len(inference.inputs_columns))
                            },
                            "outputs": {
                                inference.outputs_columns[column]: inference.outputs[row][column]
                                for column in range(len(inference.outputs_columns))
                            },
                        },
                    )

                    yield avro_inference

        self._app.agent(self._source_topic, sink=[self._target_topic])(agent)
