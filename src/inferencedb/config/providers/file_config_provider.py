from pathlib import Path

import yaml

from inferencedb.registry.decorators import config_provider
from .config_provider import ConfigProvider


@config_provider("file")
class FileConfigProvider(ConfigProvider):
    """File config provider."""

    def __init__(self, file_path: Path):
        """Initializes a FileConfigProvider.

        Args:
            file_path: Config file path.
        """
        super().__init__()
        self.file_path = file_path

    async def run(self):
        """See base class."""
        # The file config provider does not support dynamic updates
        with open(self.file_path, "r") as config_file:
            config = yaml.safe_load(config_file)

        self.update_config(config)
