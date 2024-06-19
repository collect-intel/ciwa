# config/config_manager.py

"""
This module provides the ConfigManager class for managing configuration settings.

The ConfigManager class supports initializing configurations from a file,
a dictionary, or keyword args.

Example usage
  config = ConfigManager(config_path="path/to/config.yaml")
  config = ConfigManager(config=config_dict)
  config = ConfigManager(sessions=[
  {"topics": [
    {"title": "Topic Title",
    "Description": "topic description"}
    ]],
    default_topic_settings={
    "voting_method": {"type": "RankingCompare"}})
"""

from typing import Dict, Any
import yaml


class ConfigManager:
    """
    A class to manage configuration settings.

    Supports initialization from a file, a dictionary, or keyword arguments.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, config_path=None, config=None, **kwargs):
        if config_path:
            self._init_from_file(config_path)
        elif config:
            self._init_from_dict(config)
        else:
            self._init_from_kwargs(**kwargs)

    def _init_from_file(self, config_path: str) -> None:
        """
        Initialize the configuration from a YAML file.

        Args:
            config_path (str): The path to the configuration file.
        """
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def _init_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Initialize the configuration from a dictionary.

        Args:
            config_dict (Dict[str, Any]): The configuration dictionary.
        """
        self.config = config_dict

    def _init_from_kwargs(self, **kwargs) -> None:
        """
        Initialize the configuration from keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        self.config = kwargs

    def get_config(self, path: str) -> Any:
        """
        Retrieve a configuration value by its dot-separated path.

        Args:
            path (str): The dot-separated path to the configuration value.

        Returns:
            Any: The configuration value.
        """
        keys = path.split(".")
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value
