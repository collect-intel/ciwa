# tests/test_prompt_loader.py

import pytest
from unittest.mock import patch, mock_open
import yaml
from ciwa.utils.prompt_loader import load_prompts, get_prompts


@pytest.fixture
def mock_yaml_content():
    return """
    BaseClass:
        system_message: "Base system message"
        submission_prompt: "Base submission prompt"

    DerivedClass:
        submission_prompt: "Derived submission prompt"

    StandaloneClass:
        custom_prompt: "Standalone custom prompt"
    """


@pytest.fixture
def mock_file(mock_yaml_content):
    return mock_open(read_data=mock_yaml_content)


def test_load_prompts(mock_file):
    with patch("builtins.open", mock_file), patch("os.path.exists", return_value=True):
        prompts = load_prompts("dummy_path.yaml")

    assert "BaseClass" in prompts
    assert "DerivedClass" in prompts
    assert "StandaloneClass" in prompts
    assert prompts["BaseClass"]["system_message"] == "Base system message"
    assert prompts["DerivedClass"]["submission_prompt"] == "Derived submission prompt"
    assert prompts["StandaloneClass"]["custom_prompt"] == "Standalone custom prompt"


def test_get_prompts_base_class(mock_file):
    class BaseClass:
        pass

    with patch("builtins.open", mock_file), patch("os.path.exists", return_value=True):
        prompts = get_prompts(BaseClass)

    assert "system_message" in prompts
    assert "submission_prompt" in prompts
    assert prompts["system_message"] == "Base system message"
    assert prompts["submission_prompt"] == "Base submission prompt"


def test_get_prompts_derived_class(mock_file):
    class BaseClass:
        pass

    class DerivedClass(BaseClass):
        pass

    with patch("builtins.open", mock_file), patch("os.path.exists", return_value=True):
        prompts = get_prompts(DerivedClass)

    assert "system_message" in prompts
    assert "submission_prompt" in prompts
    assert prompts["system_message"] == "Base system message"
    assert prompts["submission_prompt"] == "Derived submission prompt"


def test_get_prompts_standalone_class(mock_file):
    class StandaloneClass:
        pass

    with patch("builtins.open", mock_file), patch("os.path.exists", return_value=True):
        prompts = get_prompts(StandaloneClass)

    assert "custom_prompt" in prompts
    assert prompts["custom_prompt"] == "Standalone custom prompt"


def test_get_prompts_nonexistent_class(mock_file):
    class NonexistentClass:
        pass

    with patch("builtins.open", mock_file), patch("os.path.exists", return_value=True):
        prompts = get_prompts(NonexistentClass)

    assert prompts == {}


def test_load_prompts_file_not_found():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            load_prompts("nonexistent_file.yaml")


def test_get_prompts_inheritance_order(mock_file):
    class GrandparentClass:
        pass

    class ParentClass(GrandparentClass):
        pass

    class ChildClass(ParentClass):
        pass

    mock_yaml_content = """
    GrandparentClass:
        prompt1: "Grandparent prompt 1"
        prompt2: "Grandparent prompt 2"

    ParentClass:
        prompt2: "Parent prompt 2"
        prompt3: "Parent prompt 3"

    ChildClass:
        prompt3: "Child prompt 3"
        prompt4: "Child prompt 4"
    """

    with patch("builtins.open", mock_open(read_data=mock_yaml_content)), patch(
        "os.path.exists", return_value=True
    ):
        prompts = get_prompts(ChildClass)

    assert prompts["prompt1"] == "Grandparent prompt 1"
    assert prompts["prompt2"] == "Parent prompt 2"
    assert prompts["prompt3"] == "Child prompt 3"
    assert prompts["prompt4"] == "Child prompt 4"
