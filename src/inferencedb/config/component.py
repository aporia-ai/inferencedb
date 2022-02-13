from typing import Any, Dict, Optional

from inferencedb.base_model import BaseModel


class ComponentConfig(BaseModel):
    """Generic config for registered components."""

    type: str
    config: Optional[Dict[str, Any]] = None
