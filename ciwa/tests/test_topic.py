# ciwa/tests/test_topic.py

import pytest
from ciwa.models.topic import TopicFactory
from ciwa.models.session import Session
from ciwa.models.submission import Submission
from ciwa.models.participants.participant_factory import ParticipantFactory


@pytest.fixture
def session():
    return Session(
        process=None,
        name="Test Session",
        description="A test session",
        topics_config=[],
        default_topic_settings={},
        participants_config=[],
    )


@pytest.fixture
def topic_config():
    return {
        "title": "Test Topic",
        "description": "A test topic",
        "voting_method": {"type": "RankingCompare"},
    }


@pytest.fixture
def participant():
    participant_config = {"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}
    return ParticipantFactory.create_participant(**participant_config)


def test_topic_creation(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    assert topic.title == "Test Topic"
    assert topic.description == "A test topic"
    assert topic.voting_manager.voting_method.type == "RankingCompare"


@pytest.mark.asyncio
async def test_add_submission(session, topic_config, participant):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    submission_content = "This is a test submission."
    submission = Submission(
        topic=topic, participant=participant, content=submission_content
    )

    await topic.add_submission(submission)
    assert len(topic.submissions) == 1
    assert topic.submissions[0].content == submission_content
    assert topic.submissions[0].participant == participant


def test_voting_manager_initialization(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    assert topic.voting_manager is not None
    assert topic.voting_manager.topic == topic


if __name__ == "__main__":
    pytest.main()
