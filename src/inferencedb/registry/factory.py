from typing import Any, Dict, Optional

from .registry import get_registry, RegisteredObjectType


def create_registered_object(
    object_type: RegisteredObjectType, name: str, params: Optional[Dict[str, Any]] = None
) -> Any:
    """Creates an object based on registry definitions.

    Args:
        object_type: Object type
        name: Object name
        config: Object config

    Returns:
        A new new object using the config.
    """
    registry = get_registry()
    registered_object = registry.get(object_type=object_type, name=name)

    return registered_object.create_instance(params=params)
