from dataclasses import dataclass
from inspect import isclass, Signature, signature
from typing import Any, Callable, Dict, Optional, Tuple, Type

from pydantic.main import create_model

from inferencedb.base_model import BaseModel


class RegisteredObjectMetadata:
    """Base class for registered object metadata."""

    pass


@dataclass(frozen=True)
class RegisteredObject:
    """Registered callable object."""

    callable: Callable
    metadata: Optional[RegisteredObjectMetadata] = None

    @property
    def signature(self) -> Signature:
        """Returns the signature of the callable."""
        return signature(self.callable)

    @property
    def parameters(self) -> Dict[str, Tuple[type, Any]]:
        """Returns the callable parameters as a name -> (type, default) mapping."""
        params_dict = {}
        for param_name, param in self.signature.parameters.items():
            param_default = ...
            if param.default is not param.empty:
                param_default = param.default

            params_dict[param_name] = (param.annotation, param_default)

        return params_dict

    @property
    def parameters_model(self) -> Type[BaseModel]:
        """Generates a pydantic model from the callable parameters."""
        return create_model(
            f"{callable.__name__}_params",
            **self.parameters,  # type: ignore
            __base__=BaseModel,
        )

    def create_instance(self, params: Optional[dict] = None) -> Any:
        """Creates an instance of the registered object.

        Args:
            params: Constructor parameters.

        Returns:
            An instance of the registered object class.
        """
        if not isclass(self.callable):
            raise TypeError(f"Cannot create instance of non-class object {self.callable}.")

        if params is None:
            params = {}

        validated_params = self.parameters_model(**params)  # type: ignore

        return self.callable(**validated_params.dict())
