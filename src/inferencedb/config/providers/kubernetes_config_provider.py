from pathlib import Path

from inferencedb.registry.decorators import config_provider
from .config_provider import ConfigProvider

@config_provider("kubernetes")
class KubernetesConfigProvider(ConfigProvider):
    """Kubernetes config provider."""

    def __init__(self):
        """Initializes a KubernetesConfigProvider."""
        super().__init__()

    async def run(self):
        """See base class."""
        self.update_config({
            "api_version": "v1alpha1",
            "kind": "Config",
            "inference_loggers": [{
                "schema_provider": {
                    "type": "kserve",
                    "config": {
                        "protocol": "v2",
                        "model_name": "my-model",
                        "namespace": "default", 
                    }
                },
                "topic": "knative-broker-default-my-model-kafka-broker",
                "event_processor": {
                    "type": "kserve",
                    "config": {
                        "protocol": "v2",
                        "partitions": 10,
                    }
                },
                "destination": {
                    "type": "s3-parquet",
                    "config": {
                        "url": "s3://blablabla.parquet",
                    },
                },
            }],
        })
