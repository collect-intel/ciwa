# ciwa/tests/test_process_factory.py

import pytest
from ciwa.models.process import ProcessFactory
from ciwa.config import ConfigManager


@pytest.fixture
def process_config():
    return {
        "name": "Test Process",
        "description": "A test process",
        "sessions": [
            {
                "name": "Test Session",
                "description": "A test session",
                "topics": [
                    {
                        "title": "Test Topic",
                        "description": "A test topic",
                        "voting_method": {"type": "RankingCompare"},
                    }
                ],
                "participants": [
                    {"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}
                ],
            }
        ],
        "default_session_settings": {},
    }


def test_create_process(process_config):
    process = ProcessFactory.create_process(config=process_config)

    assert process.name == "Test Process"
    assert process.description == "A test process"
    assert len(process.pending_sessions) == 1
    assert process.pending_sessions[0].name == "Test Session"
    assert process.pending_sessions[0].description == "A test session"
    assert len(process.pending_sessions[0].topics) == 1
    assert process.pending_sessions[0].topics[0].title == "Test Topic"
    assert process.pending_sessions[0].topics[0].description == "A test topic"
    assert len(process.pending_sessions[0].participants) == 1


if __name__ == "__main__":
    pytest.main()
