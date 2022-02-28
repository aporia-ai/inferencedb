import asyncio
import logging
import os
from pathlib import Path
import ssl
from typing import List, Optional

import aiohttp

from inferencedb.registry.decorators import config_provider
from .config_provider import ConfigProvider

SERVICE_TOKEN_FILENAME = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
SERVICE_CERT_FILENAME = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
NAMESPACE_FILENAME = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")


@config_provider("kubernetes")
class KubernetesConfigProvider(ConfigProvider):
    """Kubernetes config provider."""

    def __init__(
        self,
        is_namespaced: bool,
        polling_interval_sec: int = 5,
    ):
        """Initializes a KubernetesConfigProvider."""
        super().__init__()
        self._is_namespaced = is_namespaced
        self._polling_interval_sec = polling_interval_sec

        # Read Kubernetes in-cluster token.
        with open(SERVICE_TOKEN_FILENAME) as token_file:
            token = token_file.read()

        # Read Kubernetes namespace.
        with open(NAMESPACE_FILENAME) as namespace_file:
            self._namespace = namespace_file.read()

        # Prepare aiohttp session.
        ssl_context = ssl.create_default_context(cafile=str(SERVICE_CERT_FILENAME))
        connector = aiohttp.TCPConnector(ssl_context=ssl_context, verify_ssl=True)

        # URL Prefix - for some reason this doesn't work with aiohttp's base_url
        self._url_prefix = "/apis/inferencedb.aporia.com/v1alpha1"
        if is_namespaced:
            self._url_prefix += f"/namespaces/{self._namespace}"

        # The KUBERNETES_SERVICE_HOST and KUBERNETES_SERVICE_PORT environment variables are automatically
        # defined by Kubernetes to enable pods to easily access the Kubernetes API.
        host = os.environ["KUBERNETES_SERVICE_HOST"]
        port = os.environ["KUBERNETES_SERVICE_PORT"]

        # HTTP session configuration
        self._session_config = {
            "base_url": f"https://{host}:{port}",
            "headers": {"Authorization": f"Bearer {token}"},
            "connector": connector,
        }

    async def run(self):
        """See base class."""
        async with aiohttp.ClientSession(**self._session_config) as session:
            while True:
                config = await self._fetch_config(session)
                if config is not None:
                    self.update_config(config)

                await asyncio.sleep(self._polling_interval_sec)

    async def _fetch_config(self, session: aiohttp.ClientSession) -> Optional[dict]:
        """Fetch configuration from Kubernetes resources.

        Args:
            session: AIOHttp session to use

        Returns:
            Configuration dict
        """
        
        try:
            k8s_inference_loggers = await self._get_k8s_resources(session, "inferenceloggers")
        except RuntimeError:
            logging.error("Fetching K8s resources failed.", exc_info=True)
            return None

        # Iterate all InferenceLogger resources
        try:
            return {
                "api_version": "v1alpha1",
                "kind": "Config",
                "inferenceLoggers": [{
                    "name": f'{item["metadata"]["namespace"]}-{item["metadata"]["name"]}',
                    "topic": item["spec"]["topic"],
                    "events": item["spec"]["events"],
                    "schema": item["spec"].get("schema"),
                    "filters": item["spec"].get("filters"),
                    "destination": item["spec"]["destination"],
                } for item in k8s_inference_loggers],
            }
        except KeyError:
            logging.error("Invalid configuration format.", exc_info=True)
            return None

    async def _get_k8s_resources(
        self, session: aiohttp.ClientSession, plural_name: str
    ) -> List[dict]:
        """Fetch Kubernetes resources.

        Args:
            session: AIOHttp session to use
            plural_name: Plural lower case name of the resource (e.g pods)

        Returns:
            List of the resources.
        """
        async with session.get(f"{self._url_prefix}/{plural_name}") as response:
            # All 2XX status codes (OK, CREATED, etc.) are considered success responses.
            # 3XX status codes are considered failures because we don't really handle redirects,
            # proxies, etc. All other statuses are obviously errors.
            if response.status < 200 or response.status >= 300:
                # This always raises an exception
                raise RuntimeError(
                    f"Failed to fetch K8s {plural_name} resources (HTTP status: {response.status})"
                )

            response_content = await response.json()

        if "items" not in response_content:
            raise RuntimeError("Invalid K8s API response (couldn't find 'items' in JSON)")

        return response_content["items"]
