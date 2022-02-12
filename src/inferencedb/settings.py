from argparse import ArgumentParser
import json
from typing import Any, Dict

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Execution settings."""

    kafka_broker: str
    kafka_schema_registry_url: str
    kafka_connect_url: str
    config_provider_args: Dict[str, Any]
    config_provider: str = "kubernetes"
    log_level: str = "WARNING"
    enable_pretty_logs: bool = False
    enable_dev_mode: bool = False

    class Config:
        """Execution settings config."""

        env_prefix = "INFERENCEDB_"
