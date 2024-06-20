# tests/test_score_compare.py

import pytest
from ciwa.models.voting_methods import ScoreCompare
from ciwa.models.voting_results import CompareVotingResults
from ciwa.tests.utils.model_utils import create_submission


@pytest.fixture
def score_compare_voting_method():
    return ScoreCompare(start_value=1, end_value=10)


def test_score_compare_voting_method_initialization(score_compare_voting_method):
    assert score_compare_voting_method is not None


def test_score_compare_voting_method_get_vote_schema(score_compare_voting_method):
    schema = score_compare_voting_method.get_vote_schema(num_submissions=2)
    assert isinstance(schema, dict)


def test_score_compare_voting_method_process_votes(score_compare_voting_method):
    voting_results = CompareVotingResults()
    submission_ids = ["submission1", "submission2"]
    submissions = [create_submission(id=id) for id in submission_ids]
    score_compare_voting_method.get_vote_prompt(submissions)

    votes = {
        "participant1": {"vote": {"submission_1": 3, "submission_2": 5}},
        "participant2": {"vote": {"submission_1": 1, "submission_2": 6}},
        "participant3": {"vote": {"submission_1": 2, "submission_2": 7}},
    }

    for participant_id, vote_data in votes.items():
        voting_results.add_vote(participant_id, vote_data)

    results = score_compare_voting_method.process_votes(voting_results, submission_ids)

    assert isinstance(results, dict)
    assert "submission1" in results
    assert "submission2" in results
    assert results == {"submission1": 2.0, "submission2": 6.0}
