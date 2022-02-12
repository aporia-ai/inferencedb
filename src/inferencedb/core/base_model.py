from pydantic import BaseModel as PydanticBaseModel
from pydantic.main import Extra


class BaseModel(PydanticBaseModel):
    """Base class for all pydantic models.

    This class was added to change the pydantic default behavior globally.
    Reference: https://pydantic-docs.helpmanual.io/usage/model_config/#change-behaviour-globally
    """

    class Config:
        """Configuration for BaseModel."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
