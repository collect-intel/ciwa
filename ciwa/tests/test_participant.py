# ciwa/tests/test_participant.py

import pytest
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.session import Session
from ciwa.models.topic import TopicFactory
from ciwa.models.submission import Submission


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
def topic(session):
    topic_config = {
        "title": "Test Topic",
        "description": "A test topic",
        "voting_method": {"type": "RankingCompare"},
    }
    return TopicFactory.create_topic(session=session, **topic_config)


def test_participant_creation():
    participant_config = {"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}
    participant = ParticipantFactory.create_participant(**participant_config)
    assert participant is not None
    assert participant.model == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_participant_interaction(topic):
    participant_config = {"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}
    participant = ParticipantFactory.create_participant(**participant_config)
    submission_content = "This is a test submission."
    submission = Submission(
        topic=topic, participant=participant, content=submission_content
    )
    await topic.add_submission(submission)
    assert len(topic.submissions) == 1
    assert topic.submissions[0].content == submission_content
    assert topic.submissions[0].participant == participant


if __name__ == "__main__":
    pytest.main()
