from typing import Any, Dict, Optional

from inferencedb.registry.factory import create_registered_object
from inferencedb.registry.registry import RegisteredObjectType
from .event_processor import EventProcessor


def create_event_processor(type: str, params: Optional[Dict[str, Any]] = None) -> EventProcessor:
    """Creates an EventProcessor object.

    Args:
        type: EventProcessor type
        params: EventProcessor parameters

    Returns:
        EventProcessor object
    """
    return create_registered_object(
        object_type=RegisteredObjectType.EVENT_PROCESSOR, name=type, params=params
    )
