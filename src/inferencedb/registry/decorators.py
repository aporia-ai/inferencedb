from typing import Callable, Union

from .registry import get_registry, RegisteredObjectType


def event_processor(name: str) -> Callable[[Callable], Callable]:
    """Decorator for registering event processors.

    Args:
        name: User friendly name for the event processor.

    Returns:
        Decorated class.
    """

    def _decorator(callable: Callable) -> Callable:
        registry = get_registry()
        registry.register(
            object_type=RegisteredObjectType.EVENT_PROCESSOR, name=name, callable=callable
        )
        return callable

    return _decorator


def destination(name: str) -> Callable[[Callable], Callable]:
    """Decorator for registering destinations.

    Args:
        name: User friendly name for the destination.

    Returns:
        Decorated class.
    """

    def _decorator(callable: Callable) -> Callable:
        registry = get_registry()
        registry.register(object_type=RegisteredObjectType.DESTINATION, name=name, callable=callable)
        return callable

    return _decorator


def config_provider(name: str) -> Callable[[Callable], Callable]:
    """Decorator for registering config providers.

    Args:
        name: User friendly name for the config provider.

    Returns:
        Decorated class.
    """

    def _decorator(callable: Callable) -> Callable:
        registry = get_registry()
        registry.register(
            object_type=RegisteredObjectType.CONFIG_PROVIDER, name=name, callable=callable
        )
        return callable

    return _decorator


def schema_provider(name: str) -> Callable[[Callable], Callable]:
    """Decorator for registering schema providers.

    Args:
        name: User friendly name for the schemas provider.

    Returns:
        Decorated class.
    """

    def _decorator(callable: Callable) -> Callable:
        registry = get_registry()
        registry.register(
            object_type=RegisteredObjectType.SCHEMA_PROVIDER, name=name, callable=callable
        )
        return callable

    return _decorator
