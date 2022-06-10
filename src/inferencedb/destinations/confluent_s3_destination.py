import asyncio
import logging
from typing import Any, Dict
from urllib.parse import urlparse

import aiohttp

from inferencedb.destinations.destination import Destination
from inferencedb.registry.decorators import destination
from inferencedb.settings import Settings


class ConnectorAlreadyExistsException(Exception):
    pass


CONFLUENT_KAFKA_CONNECT_FORMATS = {
    "parquet": "io.confluent.connect.s3.format.parquet.ParquetFormat",
}

DEFAULT_HTTP_TIMEOUT_SEC = 5


@destination("confluent-s3")
class ConfluentS3Destination(Destination):
    def __init__(self, logger_name: str, topic: str, config: Dict[str, Any]):
        self._logger_name = logger_name
        self._topic = topic
        self._config = config

    async def create_connector(self):
        settings = Settings()
        url = urlparse(self._config["url"])

        connector_name = f"inferencedb-{self._logger_name}"
        connector_config =  {
            "connector.class": "io.confluent.connect.s3.S3SinkConnector",
            "storage.class": "io.confluent.connect.s3.storage.S3Storage",
            "s3.region": self._config["awsRegion"],
            "s3.bucket.name": url.netloc,
            "topics.dir": url.path.strip("/"),
            "flush.size": "2",
            "rotate.schedule.interval.ms": "20000",
            "auto.register.schemas": "false",
            "tasks.max": "1",
            "s3.part.size": "5242880",
            "timezone": "UTC",
            "parquet.codec": "snappy",
            "topics": self._topic,
            "s3.credentials.provider.class": "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
            "format.class": CONFLUENT_KAFKA_CONNECT_FORMATS[self._config["format"]],
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "key.converter": "org.apache.kafka.connect.storage.StringConverter",
            "schema.registry.url": settings.kafka_schema_registry_url,
            "value.converter.schema.registry.url": settings.kafka_schema_registry_url,
            **self._config.get("connector", {})
        }

        async with aiohttp.ClientSession(
            base_url=settings.kafka_connect_url,
            timeout=aiohttp.ClientTimeout(total=DEFAULT_HTTP_TIMEOUT_SEC),
        ) as session:
            await self._upsert_connector(session, connector_name, connector_config)

    async def _upsert_connector(self, session: aiohttp.ClientSession, connector_name: str, connector_config: dict):
        for _ in range(10):
            async with session.put(
                url=f"/connectors/{connector_name}/config",
                json=connector_config,
            ) as response:
                if response.status in (201, 200):
                    return
                elif response.status == 409:
                    # Kafka connect rebalance
                    await asyncio.sleep(3)
                    continue
                else:
                    raise RuntimeError(f"Could not create connector: {connector_name}, status: {response.status}")
        
        raise RuntimeError(f"Could not create connector because of Kafka Connect rebalance.")
