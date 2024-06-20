# tests/test_ranking_comapre.py

import pytest
from ciwa.models.voting_methods import RankingCompare
from ciwa.models.voting_results import CompareVotingResults
from ciwa.tests.utils.model_utils import create_submission


@pytest.fixture
def ranking_compare_voting_method():
    return RankingCompare()


def test_ranking_compare_voting_method_initialization(ranking_compare_voting_method):
    assert ranking_compare_voting_method is not None


def test_ranking_compare_voting_method_get_vote_schema(ranking_compare_voting_method):
    schema = ranking_compare_voting_method.get_vote_schema(num_submissions=3)
    assert isinstance(schema, dict)


def test_ranking_compare_voting_method_process_votes(ranking_compare_voting_method):
    voting_results = CompareVotingResults()
    submission_ids = ["submission1", "submission2", "submission3"]
    submissions = [create_submission(id=id) for id in submission_ids]
    ranking_compare_voting_method.get_vote_prompt(submissions)

    votes = {
        "participant1": {"vote": [1, 2, 3]},
        "participant2": {"vote": [2, 1, 3]},
        "participant3": {"vote": [3, 2, 1]},
    }

    for participant_id, vote_data in votes.items():
        voting_results.add_vote(participant_id, vote_data)

    results = ranking_compare_voting_method.process_votes(
        voting_results, submission_ids
    )

    assert isinstance(results, dict)
    assert "submission1" in results
    assert "submission2" in results
    assert results == {"submission2": 0.667, "submission1": 1.0, "submission3": 1.333}
