# tests/utils/model_utils.py

"""
This module provides utility functions for creating model instances for testing purposes.
"""
from ciwa.models.process import Process
from ciwa.models.session import Session
from ciwa.models.topic import TopicFactory
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.submission import Submission


def create_process(id=None, **kwargs):
    process = Process(
        name=kwargs.get("name", "Test Process"),
        description=kwargs.get("description", "A test process"),
    )
    if id is not None:
        process._uuid = id
    return process


def create_session(id=None, **kwargs):
    session = Session(
        process=kwargs.get("process", create_process()),
        name=kwargs.get("name", "Test Session"),
        description=kwargs.get("description", "A test session"),
        topics_config=kwargs.get("topics_config", []),
        default_topic_settings=kwargs.get("default_topic_settings", {}),
        participants_config=kwargs.get("participants_config", []),
    )
    session.process.current_session = session
    if id is not None:
        session._uuid = id
    return session


def create_topic(session=None, id=None, **kwargs):
    if session is None:
        session = create_session()
    topic_config = {
        "title": kwargs.get("title", "Test Topic"),
        "description": kwargs.get("description", "A test topic"),
        "voting_method": kwargs.get("voting_method", {"type": "RankingCompare"}),
    }
    topic = TopicFactory.create_topic(session=session, **topic_config)
    if id is not None:
        topic._uuid = id
    return topic


def create_participant(id=None, process=None, **kwargs):
    if process is None:
        process = create_session().process
    participant_config = {
        "type": kwargs.get("type", "LLMAgentParticipant"),
        "model": kwargs.get("model", "gpt-3.5-turbo"),
    }
    participant = ParticipantFactory.create_participant(
        process=process, **participant_config
    )
    if id is not None:
        participant._uuid = id
    return participant


def create_submission(topic=None, participant=None, id=None, **kwargs):
    if topic is None:
        topic = create_topic()
    if participant is None:
        participant = create_participant()
    content = kwargs.get("content", "This is a test submission.")
    submission = Submission(topic=topic, participant=participant, content=content)
    if id is not None:
        submission._uuid = id
    return submission
