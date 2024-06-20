# ciwa/tests/test_voting_manager.py

import pytest
from ciwa.models.voting_manager import VotingManagerFactory
from ciwa.models.topic import TopicFactory
from ciwa.models.session import Session
from ciwa.models.submission import Submission
from ciwa.models.participants import ParticipantFactory


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


@pytest.fixture
def participant():
    participant_config = {"type": "LLMAgentParticipant", "model": "gpt-3.5-turbo"}
    return ParticipantFactory.create_participant(**participant_config)


@pytest.mark.asyncio
async def test_voting_manager_initialization(topic):
    voting_manager = VotingManagerFactory.create_voting_manager(
        voting_method="RankingCompare", topic=topic
    )
    assert voting_manager is not None
    assert voting_manager.topic == topic


@pytest.mark.asyncio
async def test_add_submission_to_voting_manager(topic, participant):
    voting_manager = VotingManagerFactory.create_voting_manager(
        voting_method="RankingCompare", topic=topic
    )
    submission_content = "This is a test submission."
    submission = Submission(
        topic=topic, participant=participant, content=submission_content
    )

    await topic.add_submission(submission)
    assert len(voting_manager.topic.submissions) == 1
    assert voting_manager.topic.submissions[0].content == submission_content
    assert voting_manager.topic.submissions[0].participant == participant


if __name__ == "__main__":
    pytest.main()
