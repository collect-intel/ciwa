# tests/test_score_label.py

import pytest
from ciwa.models.voting_methods import ScoreLabel
from ciwa.models.voting_results import LabelVotingResults


@pytest.fixture
def score_label_voting_method():
    return ScoreLabel(start_value=1, end_value=10)


def test_score_label_voting_method_initialization(score_label_voting_method):
    assert score_label_voting_method is not None


def test_score_label_voting_method_get_vote_schema(score_label_voting_method):
    schema = score_label_voting_method.get_vote_schema()
    assert isinstance(schema, dict)


def test_score_label_voting_method_process_votes(score_label_voting_method):
    voting_results = LabelVotingResults()
    submission_ids = ["submission1", "submission2"]
    vote_data = {
        "submission1": {"vote": 5},
        "submission2": {"vote": 3},
    }
    participant_id = "participant1"
    voting_results.add_vote(participant_id, vote_data)

    results = score_label_voting_method.process_votes(voting_results, submission_ids)
    assert isinstance(results, dict)
    assert results["submission1"]["average_score"] == 5
    assert results["submission2"]["average_score"] == 3

    # Add more votes to test the average score
    voting_results.add_vote("participant2", {"submission1": {"vote": 4}})
    results = score_label_voting_method.process_votes(voting_results, submission_ids)
    assert results["submission1"]["average_score"] == 4.5
    assert results["submission2"]["average_score"] == 3
