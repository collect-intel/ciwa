import pytest
from ciwa.models.topic import TopicFactory, Topic
from ciwa.models.session import Session
from ciwa.models.submission import Submission
from ciwa.models.participants import ParticipantFactory
from unittest.mock import MagicMock


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


@pytest.mark.asyncio
async def test_add_invalid_submission(session, topic_config, participant):
    topic_config["submission_validator"] = MagicMock(return_value=False)
    topic_config["submission_invalid_message"] = "Invalid submission."

    topic = TopicFactory.create_topic(session=session, **topic_config)

    submission_content = "This is a test submission."
    submission = Submission(
        topic=topic, participant=participant, content=submission_content
    )

    await topic.add_submission(submission)
    assert len(topic.submissions) == 0


def test_voting_manager_initialization(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    assert topic.voting_manager is not None
    assert topic.voting_manager.topic == topic


def test_set_submission_content_schema(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    new_schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
    }
    topic.set_submission_content_schema(new_schema)
    assert topic.submission_content_schema == new_schema


def test_set_invalid_submission_content_schema(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    invalid_schema = {"type": "invalid_type"}
    with pytest.raises(Exception):
        topic.set_submission_content_schema(invalid_schema)


@pytest.mark.asyncio
async def test_add_submission_with_content_schema(session, topic_config, participant):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    topic.set_submission_content_schema({"type": "string"})

    submission_content = "This is a test submission."
    submission = Submission(
        topic=topic, participant=participant, content=submission_content
    )

    await topic.add_submission(submission)
    assert len(topic.submissions) == 1
    assert topic.submissions[0].content == submission_content
    assert topic.submissions[0].participant == participant
    assert topic.submissions[0].topic == topic


def test_topic_to_json(session, topic_config):
    topic = TopicFactory.create_topic(session=session, **topic_config)
    topic_json = topic.to_json()
    assert topic_json["uuid"] == str(topic.uuid)
    assert topic_json["title"] == topic.title
    assert topic_json["description"] == topic.description
    assert (
        topic_json["voting_method"]
        == topic.voting_manager.voting_method.__class__.__name__
    )
    assert "submissions" in topic_json


if __name__ == "__main__":
    pytest.main()
