# tests/test_enum_label.py

import pytest
from ciwa.models.voting_methods.enum_label import EnumLabel
from ciwa.models.voting_results import LabelVotingResults


@pytest.fixture
def enum_labels():
    return ["Option1", "Option2", "Option3"]


@pytest.fixture
def enum_label_voting_method(enum_labels):
    return EnumLabel(enum_values=enum_labels)


def test_enum_label_voting_method_initialization(enum_label_voting_method):
    assert enum_label_voting_method is not None


def test_enum_label_voting_method_get_vote_schema(enum_label_voting_method):
    schema = enum_label_voting_method.get_vote_schema()
    assert isinstance(schema, dict)


def test_enum_label_voting_method_process_votes(enum_label_voting_method):
    voting_results = LabelVotingResults()
    submission_ids = ["submission1", "submission2"]
    vote_data = {
        "submission1": {"vote": "Option1"},
        "submission2": {"vote": "Option2"},
    }
    participant_id = "participant1"
    voting_results.add_vote(participant_id, vote_data)

    results = enum_label_voting_method.process_votes(voting_results, submission_ids)
    assert isinstance(results, dict)
    assert results["submission1"] == {"Option1": 1, "Option2": 0, "Option3": 0}
    assert results["submission2"] == {"Option1": 0, "Option2": 1, "Option3": 0}

    # Add more votes to test the count of each label
    voting_results.add_vote("participant2", {"submission1": {"vote": "Option1"}})
    voting_results.add_vote("participant3", {"submission1": {"vote": "Option2"}})
    results = enum_label_voting_method.process_votes(voting_results, submission_ids)
    assert results["submission1"] == {"Option1": 2, "Option2": 1, "Option3": 0}
    assert results["submission2"] == {"Option1": 0, "Option2": 1, "Option3": 0}
