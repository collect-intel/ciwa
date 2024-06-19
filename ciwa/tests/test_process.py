# ciwa/tests/test_process.py

import pytest
from ciwa.config.config_manager import ConfigManager
from ciwa.models.process import ProcessFactory
from ciwa.models.owner import Owner


@pytest.fixture
def process():
    config_manager = ConfigManager(config_path="ciwa/tests/config/settings.yaml")
    process_config = config_manager.get_config("process")
    return ProcessFactory.create_process(config=process_config)


def test_process_creation(process):
    assert process.name == "Test CIwA Process from file"
    assert process.description == "A test process for CIwA from file"
    assert len(process.pending_sessions) > 0


def test_add_owner(process):
    owner = Owner(name="Test Owner", email="test@example.com")
    process.add_owner(owner)
    assert len(process.owners) == 1
    assert process.owners[0].name == "Test Owner"


def test_add_session(process):
    new_session_config = {
        "name": "New Session",
        "description": "A new test session",
        "topics": [
            {
                "title": "New Topic",
                "description": "Description of new topic",
                "voting_method": {"type": "RankingCompare"},
            }
        ],
        "participants": [{"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}],
    }
    process.add_session(new_session_config)
    print(f"Pending sessions count: {len(process.pending_sessions)}")
    print(f"Pending sessions: {process.pending_sessions}")
    assert len(process.pending_sessions) > 1
