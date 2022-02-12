from typing import Any, Dict, Optional

from inferencedb.registry.factory import create_registered_object
from inferencedb.registry.registry import RegisteredObjectType
from .schema_provider import SchemaProvider


def create_schema_provider(type: str, params: Optional[Dict[str, Any]] = None) -> SchemaProvider:
    """Creates an SchemaProvider object.

    Args:
        type: SchemaProvider type
        params: SchemaProvider parameters

    Returns:
        SchemaProvider object
    """
    return create_registered_object(
        object_type=RegisteredObjectType.SCHEMA_PROVIDER, name=type, params=params
    )
