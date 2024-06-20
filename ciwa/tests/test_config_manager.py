# tests/test_config_manager.py

import pytest
from ciwa.config import ConfigManager


def test_config_manager_init_from_file():
    config_manager = ConfigManager(config_path="ciwa/tests/config/settings.yaml")
    config = config_manager.get_config("process")
    assert config["name"] == "Test CIwA Process from file"
    assert config["description"] == "A test process for CIwA from file"


def test_config_manager_init_from_dict():
    config_dict = {
        "process": {
            "name": "Test Process from dict",
            "description": "A test process from dict",
        }
    }
    config_manager = ConfigManager(config=config_dict)
    config = config_manager.get_config("process")
    assert config["name"] == "Test Process from dict"
    assert config["description"] == "A test process from dict"


def test_config_manager_init_from_kwargs():
    config_manager = ConfigManager(
        process={
            "name": "Test Process from kwargs",
            "description": "A test process from kwargs",
        }
    )
    config = config_manager.get_config("process")
    assert config["name"] == "Test Process from kwargs"
    assert config["description"] == "A test process from kwargs"
