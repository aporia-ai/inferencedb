from typing import Any, Dict, Optional

from inferencedb.registry.factory import create_registered_object
from inferencedb.registry.registry import RegisteredObjectType
from .destination import Destination


def create_destination(type: str, params: Optional[Dict[str, Any]] = None) -> Destination:
    """Creates a Destination object.

    Args:
        type: Destination type
        params: Destination parameters

    Returns:
        Destination object
    """
    return create_registered_object(
        object_type=RegisteredObjectType.DESTINATION, name=type, params=params
    )
