from enum import Enum
from inspect import signature
from typing import Callable, Dict, Optional

from .registered_object import RegisteredObject, RegisteredObjectMetadata


class RegisteredObjectType(Enum):
    """Registered object types."""

    EVENT_PROCESSOR = "event_processor"
    DESTINATION = "destination"
    CONFIG_PROVIDER = "config_provider"
    SCHEMA_PROVIDER = "schema_provider"


GENERIC_OBJECT_TYPES = [
    RegisteredObjectType.EVENT_PROCESSOR,
    RegisteredObjectType.DESTINATION,
    RegisteredObjectType.CONFIG_PROVIDER,
    RegisteredObjectType.SCHEMA_PROVIDER,
]

ObjectCollectionDict = Dict[RegisteredObjectType, Dict[str, RegisteredObject]]


class Registry:
    """Generic callable obect registry.

    Callable code objects (classes and functions) can be registered to extend
    the functionality of aporia core.

    The registry supports the following objects:
        - sources
        - destinations
        - config providers
        - schema providers

    To register an object, use the appropriate decorator (e.g @source for sources).
    """

    def __init__(self):
        """Initializes the Registry."""
        self._generic_objects: ObjectCollectionDict = {}

        for object_type in GENERIC_OBJECT_TYPES:
            self._generic_objects[object_type] = {}

    def register(
        self,
        object_type: RegisteredObjectType,
        name: str,
        callable: Callable,
        metadata: Optional[RegisteredObjectMetadata] = None,
    ):
        """Registers an object.

        Args:
            object_type: Object type
            name: Object name
            callable: Class or function callable object
            metadata: Any other metadata to store with the object
        """
        object_collection = self._generic_objects[object_type]

        if name in object_collection:
            raise ValueError(f"{object_type.value} {name} is already registered.")

        for param_name, param in signature(callable).parameters.items():
            if param.annotation is param.empty:
                raise ValueError(
                    f"Callable {callable} parameter {param_name} is missing a type annotation."
                )

        object_collection[name] = RegisteredObject(callable=callable, metadata=metadata)

    def get(self, object_type: RegisteredObjectType, name: str) -> RegisteredObject:
        """Returns a registered object.

        Args:
            object_type: Object type.
            name: Object name.

        Returns:
            The registered object.
        """
        object_collection = self._generic_objects[object_type]

        if name not in object_collection:
            raise KeyError(f"{object_type.value} {name} is not registered.")

        return object_collection[name]


registry = Registry()


def get_registry() -> Registry:
    """Returns the global registry."""
    return registry
