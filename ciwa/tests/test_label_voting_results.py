# ciwa/tests/test_label_voting_results.py

import pytest
from ciwa.models.voting_results import LabelVotingResults
from ciwa.models.voting_methods import LabelVotingMethod
from ciwa.models.submission import Submission
from ciwa.models.participants import ParticipantFactory
from ciwa.models.topic import TopicFactory
from ciwa.models.session import Session
from ciwa.tests.utils.model_utils import (
    create_session,
    create_topic,
    create_participant,
    create_submission,
)


class MockLabelVotingMethod(LabelVotingMethod):
    def get_vote_schema(self):
        return {}

    def process_votes(self, voting_results, submission_ids):
        # Implement a simple mock processing logic
        results = {submission_id: 1.0 for submission_id in submission_ids}
        return results


@pytest.fixture
def session():
    return create_session()


@pytest.fixture
def topic():
    return create_topic(title="Custom Topic", description="A custom test topic")


@pytest.fixture
def participant():
    return create_participant()


def test_label_voting_results_initialization(topic):
    voting_results = LabelVotingResults()
    assert voting_results.participants == []
    assert voting_results.votes_data == {}
    assert voting_results.aggregated_results == {}


def test_label_voting_results_add_vote(topic, participant):
    voting_results = LabelVotingResults()
    vote_data = {"submission_id": {"vote": "yes"}}
    voting_results.add_vote(participant.uuid, vote_data)

    assert participant.uuid in voting_results.participants
    assert "submission_id" in voting_results.votes_data
    assert participant.uuid in voting_results.votes_data["submission_id"]


def test_label_voting_results_process_votes(topic, participant):
    voting_results = LabelVotingResults()
    voting_method = MockLabelVotingMethod()
    vote_data = {"submission_id": {"vote": "yes"}}
    voting_results.add_vote(participant.uuid, vote_data)
    submission_ids = ["submission_id"]

    voting_results.process_votes(voting_method, submission_ids)

    # Adjust the assertion based on the specific logic of your process_votes method
    assert "submission_id" in voting_results.aggregated_results


def test_label_voting_results_to_json(topic, participant):
    voting_results = LabelVotingResults()
    vote_data = {"submission_id": {"vote": "yes"}}
    voting_results.add_vote(participant.uuid, vote_data)
    json_data = voting_results.to_json()

    assert "submissions" in json_data
    assert "aggregated_results" in json_data


if __name__ == "__main__":
    pytest.main()
