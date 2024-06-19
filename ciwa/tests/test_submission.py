# ciwa/tests/test_submission.py

import pytest
from ciwa.models.submission import Submission
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.topic import TopicFactory
from ciwa.models.session import Session

from ciwa.tests.utils.model_utils import (
    create_session,
    create_topic,
    create_participant,
    create_submission,
)


def test_submission_creation():
    topic = create_topic(title="Custom Topic", description="A custom test topic")
    participant = create_participant(model="gpt-4")
    submission = create_submission(
        topic=topic, participant=participant, content="Custom submission content"
    )
    assert submission is not None
    assert submission.content == "Custom submission content"
    assert submission.participant.model == "gpt-4"
    assert submission.topic.title == "Custom Topic"


if __name__ == "__main__":
    pytest.main()
