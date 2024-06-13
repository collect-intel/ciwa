# config/config_manager.py

import yaml
from typing import Dict, Any


class ConfigManager:
    _instance = None

    def __new__(cls, config_path=None, config=None, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            if config_path:
                cls._instance._init_from_file(config_path)
            elif config:
                cls._instance._init_from_dict(config)
            else:
                cls._instance._init_from_kwargs(**kwargs)
        return cls._instance

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
