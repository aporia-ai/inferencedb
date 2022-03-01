from typing import Any, Dict, Optional

from inferencedb.config.config import V1Alpha1Config, V1Alpha1ConfigHeader
from inferencedb.config.providers.config_provider import ConfigProvider
from inferencedb.registry.factory import create_registered_object
from inferencedb.registry.registry import RegisteredObjectType

HEADER_VERSIONS = {"v1alpha1": V1Alpha1ConfigHeader}
CONFIG_VERSIONS = {"v1alpha1": V1Alpha1Config}


def generate_config_header_from_dict(config_dict: Dict[str, Any]) -> V1Alpha1ConfigHeader:
    """Creates a config from a dictionary.

    Args:
        config_dict: The dictionary to create the config from.

    Returns:
        The config created from the dictionary.
    """
    api_version = config_dict["api_version"].lower()
    if api_version not in HEADER_VERSIONS:
        raise ValueError(
            "Unsupported API version." f"Supported versions are {list(HEADER_VERSIONS.keys())}"
        )

    header_class = HEADER_VERSIONS[api_version]
    return header_class(**config_dict)


def generate_config_from_dict(config_dict: Dict[str, Any]) -> V1Alpha1Config:
    """Creates a config from a dictionary.

    Args:
        config_dict: The dictionary to create the config from.

    Returns:
        The config created from the dictionary.
    """
    api_version = config_dict["api_version"].lower()
    if api_version not in CONFIG_VERSIONS:
        raise ValueError(
            "Unsupported API version." f"Supported versions are {list(CONFIG_VERSIONS.keys())}"
        )

    config_class = CONFIG_VERSIONS[api_version]
    return config_class(**config_dict)


def create_config_provider(name: str, params: Optional[Dict[str, Any]] = None) -> ConfigProvider:
    """Creates a config provider object.

    Args:
        name: Config provider name
        config: Config provider configuration

    Returns:
        ConfigProvider object
    """
    return create_registered_object(
        object_type=RegisteredObjectType.CONFIG_PROVIDER, name=name, params=params
    )
