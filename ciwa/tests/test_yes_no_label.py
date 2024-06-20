# tests/test_yes_no_label.py

import pytest
from ciwa.models.voting_methods import YesNoLabel
from ciwa.models.voting_results import LabelVotingResults


@pytest.fixture
def yes_no_label_voting_method():
    return YesNoLabel()


def test_yes_no_label_voting_method_initialization(yes_no_label_voting_method):
    assert yes_no_label_voting_method is not None


def test_yes_no_label_voting_method_get_vote_schema(yes_no_label_voting_method):
    schema = yes_no_label_voting_method.get_vote_schema()
    assert isinstance(schema, dict)


def test_yes_no_label_voting_method_process_votes(yes_no_label_voting_method):
    voting_results = LabelVotingResults()
    submission_ids = ["submission1", "submission2"]
    vote_data = {
        "submission1": {"vote": "yes"},
        "submission2": {"vote": "no"},
    }
    participant_id = "participant1"
    voting_results.add_vote(participant_id, vote_data)

    results = yes_no_label_voting_method.process_votes(voting_results, submission_ids)
    assert isinstance(results, dict)
    assert results["submission1"] == {"yes": 1, "no": 0}
    assert results["submission2"] == {"no": 1, "yes": 0}

    # Add more votes to test the count of each label
    voting_results.add_vote("participant2", {"submission1": {"vote": "no"}})
    voting_results.add_vote("participant3", {"submission1": {"vote": "yes"}})
    results = yes_no_label_voting_method.process_votes(voting_results, submission_ids)
    assert results["submission1"] == {"yes": 2, "no": 1}
    assert results["submission2"] == {"no": 1, "yes": 0}
