# config/config_manager.py

import yaml
from typing import Dict, Any


class ConfigManager:
    def __init__(self, config_path=None, config=None, **kwargs):
        if config_path:
            self._init_from_file(config_path)
        elif config:
            self._init_from_dict(config)
        else:
            self._init_from_kwargs(**kwargs)

    def _init_from_file(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def _init_from_dict(self, config_dict: Dict[str, Any]) -> None:
        self.config = config_dict

    def _init_from_kwargs(self, **kwargs) -> None:
        self.config = kwargs

    def get_config(self, path):
        keys = path.split(".")
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value


# Example usage
# config = ConfigManager(config_path="path/to/config.yaml")
# config = ConfigManager(config=config_dict)
# config = ConfigManager(sessions=[{"topics": [{"title":"Topic Title", "Description":"topic description"}]], default_topic_settings={"voting_method": {"type": "RankingCompare"}})
