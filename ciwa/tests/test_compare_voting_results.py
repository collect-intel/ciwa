# ciwa/tests/test_compare_voting_results.py

import pytest
from ciwa.models.voting_results import CompareVotingResults
from ciwa.models.voting_methods.voting_method import CompareVotingMethod
from ciwa.models.submission import Submission
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.topic import TopicFactory
from ciwa.models.session import Session
import datetime

from ciwa.tests.utils.model_utils import (
    create_session,
    create_topic,
    create_participant,
    create_submission,
)


class MockCompareVotingMethod(CompareVotingMethod):
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


def test_compare_voting_results_initialization(topic):
    voting_results = CompareVotingResults()
    assert voting_results.participants == []
    assert voting_results.votes_data == {}
    assert voting_results.aggregated_results == {}


def test_compare_voting_results_add_vote(topic, participant):
    voting_results = CompareVotingResults()
    vote_data = {"vote": ["submission_id1", "submission_id2"]}
    voting_results.add_vote(participant.uuid, vote_data)

    assert participant.uuid in voting_results.participants
    assert participant.uuid in voting_results.votes_data


def test_compare_voting_results_process_votes(topic, participant):
    voting_results = CompareVotingResults()
    voting_method = MockCompareVotingMethod()
    vote_data = {"vote": ["submission_id1", "submission_id2"]}
    voting_results.add_vote(participant.uuid, vote_data)
    submission_ids = ["submission_id1", "submission_id2"]

    voting_results.process_votes(voting_method, submission_ids)

    # Adjust the assertion based on the specific logic of your process_votes method
    assert "submission_id1" in voting_results.aggregated_results


def test_compare_voting_results_to_json(topic, participant):
    voting_results = CompareVotingResults()
    vote_data = {"vote": ["submission_id1", "submission_id2"]}
    voting_results.add_vote(participant.uuid, vote_data)
    json_data = voting_results.to_json()

    assert "voting_participants" in json_data
    assert "aggregated_results" in json_data


if __name__ == "__main__":
    pytest.main()
