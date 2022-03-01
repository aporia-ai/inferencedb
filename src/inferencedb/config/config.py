from typing import Any, Dict, List, Optional
from inferencedb.registry.decorators import event_processor

from pydantic import Field, Extra

from inferencedb.core.base_model import BaseModel
from .component import ComponentConfig


class InferenceLoggerConfig(BaseModel):
    """A class representing the InferenceLogger config."""

    class Config:
        """Configuration for InferenceLoggerConfig."""

        extra = Extra.forbid

    name: str 
    topic: str
    event_processor: ComponentConfig = Field(None, alias="events")
    schema_provider: Optional[ComponentConfig] = Field(None, alias="schema")
    filters: Optional[Dict[str, str]]
    destination: ComponentConfig


class V1Alpha1ConfigHeader(BaseModel):
    """A class representing the header for the config."""

    class Config:
        """Configuration for V1Alpha1ConfigHeader."""

        # Ignore extra fields, so we can parse only the header out of the entire config
        extra = Extra.ignore

    api_version: str
    kind: str


class V1Alpha1Config(V1Alpha1ConfigHeader):
    """A class representing the v1alpha1 config."""

    class Config:
        """Configuration for V1Alpha1Config."""

        extra = Extra.forbid
    
    inference_loggers: List[InferenceLoggerConfig] = []
