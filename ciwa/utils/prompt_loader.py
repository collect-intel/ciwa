# utils/prompt_loader.py
"""
Utility functions for loading prompts from a YAML file.
"""

import os
import inspect
import yaml


# Get the absolute path to the prompts.yaml file
PROMPTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "prompts.yaml"
)


def load_prompts(yaml_file: str = PROMPTS_FILE) -> dict:
    """
    Load prompts from a YAML file.
    """
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"YAML file not found: {yaml_file}")
    with open(yaml_file, "r") as file:
        prompts = yaml.safe_load(file)
    return prompts


def get_prompts(cls: type, yaml_file: str = PROMPTS_FILE) -> dict:
    """
    Get prompts for a class, merging with parent class prompts.

    Args:
        cls (type): The class type to get prompts for.
        yaml_file (str): The path to the YAML file containing the prompts.

    Returns:
        dict: The prompts for the class.
    """
    prompts = load_prompts(yaml_file)
    effective_prompts = {}
    for base in inspect.getmro(cls):
        class_name = base.__name__
        if class_name in prompts:
            effective_prompts = {**prompts[class_name], **effective_prompts}
    return effective_prompts
