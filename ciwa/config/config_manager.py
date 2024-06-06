# config/config_manager.py

import yaml


class ConfigManager:
    _instance = None

    @classmethod
    def get_instance(cls, config_path=None):
        if cls._instance is None:
            if config_path is None:
                raise ValueError(
                    "Config path must be provided for the first initialization."
                )
            cls._instance = cls(config_path)
        return cls._instance

    def __init__(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get_config(self, path):
        keys = path.split(".")
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value
