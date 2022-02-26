import asyncio
import os
import ssl
from inferencedb.registry.decorators import config_provider
from .config_provider import ConfigProvider
import aiohttp

SERVICE_TOKEN_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/token"
SERVICE_CERT_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
NAMESPACE_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"


@config_provider("kubernetes")
class KubernetesConfigProvider(ConfigProvider):
    """Kubernetes config provider."""

    def __init__(self):
        """Initializes a KubernetesConfigProvider."""
        super().__init__()

        # Read Kubernetes in-cluster token.
        with open(SERVICE_TOKEN_FILENAME) as token_file:
            token = token_file.read()

        # Read Kubernetes namespace.
        with open(NAMESPACE_FILENAME) as namespace_file:
            self._namespace = namespace_file.read()

        # Prepare aiohttp session.
        ssl_context = ssl.create_default_context(cafile=SERVICE_CERT_FILENAME)
        connector = aiohttp.TCPConnector(ssl_context=ssl_context, verify_ssl=True)
    
        self._session_config = {
            "base_url": f'https://{os.environ["KUBERNETES_SERVICE_HOST"]}:{os.environ["KUBERNETES_SERVICE_PORT"]}',
            "headers": {"Authorization": f"Bearer {token}"},
            "connector": connector,
        }

    async def run(self):
        """See base class."""
        
        async with aiohttp.ClientSession(**self._session_config) as session:
            while True:
                # Get all InferenceLogger resources from Kubernetes.
                async with session.get(f'/apis/inferencedb.aporia.com/v1alpha1/namespaces/{self._namespace}/inferenceloggers') as response:
                    result = await response.json()
                
                self.update_config({
                    "api_version": "v1alpha1",
                    "kind": "Config",
                    "inferenceLoggers": [{
                        "name": f'{item["metadata"]["namespace"]}-{item["metadata"]["name"]}',
                        "topic": item["spec"]["topic"],
                        "events": item["spec"]["events"],
                        "schema": item["spec"].get("schema"),
                        "destination": item["spec"]["destination"],
                    } for item in result["items"]],
                })

                await asyncio.sleep(5)
