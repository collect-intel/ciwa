# filename: ciwa/utils/prompt_loader.py

import yaml
import os
import inspect


def load_prompts(yaml_file="ciwa/config/prompts.yaml") -> dict:
    with open(yaml_file, "r") as file:
        prompts = yaml.safe_load(file)
    return prompts


def get_prompts(cls: type, yaml_file="ciwa/config/prompts.yaml") -> dict:
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
