# ciwa/tests/test_session_factory.py

import pytest
from ciwa.models.session import SessionFactory
from ciwa.models.process import Process
from ciwa.models.participants.participant_factory import ParticipantFactory


@pytest.fixture
def process():
    return Process(
        name="Test Process",
        description="A test process for sessions",
        session_configs=[],
    )


@pytest.fixture
def session_config():
    return {
        "name": "Test Session",
        "description": "A test session",
        "topics": [
            {
                "title": "Test Topic",
                "description": "A test topic",
                "voting_method": {"type": "RankingCompare"},
            }
        ],
        "participants": [{"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}],
    }


def test_create_session(process, session_config):
    session = SessionFactory.create_session(process=process, **session_config)
    assert session.name == "Test Session"
    assert session.description == "A test session"
    assert len(session.topics) == 1
    assert session.topics[0].title == "Test Topic"
    assert session.topics[0].description == "A test topic"
    assert len(session.participants) == 1


if __name__ == "__main__":
    pytest.main()
