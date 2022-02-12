from dataclasses import dataclass
from typing import Any, Dict, Optional

from inferencedb.core.base_model import BaseModel


class Inference(BaseModel):
    id: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
