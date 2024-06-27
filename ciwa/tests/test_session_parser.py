# tests/test_session_parser.py

import pytest
import json
import pandas as pd
from pathlib import Path
from tempfile import NamedTemporaryFile
from ciwa.utils.session_parser import (
    parse_session_json,
)


@pytest.fixture
def sample_session_data():
    return {
        "session": {
            "uuid": "test-session-uuid",
            "name": "Test Session",
            "description": "Test description",
        },
        "topics": [
            {
                "uuid": "test-topic-uuid",
                "title": "Test Topic",
                "description": "Test topic description",
                "voting_method": "RankingCompare",
                "submissions": [
                    {
                        "uuid": "test-submission-uuid",
                        "participant_uuid": "test-participant-uuid",
                        "content": "Test submission content",
                        "created_at": "2024-06-26T22:01:40.636993",
                    }
                ],
                "voting_results": {
                    "voting_participants": [
                        {
                            "uuid": "test-participant-uuid",
                            "vote": {
                                "created_at": "2024-06-26T22:01:57.617432",
                                "vote": [1, 2, 3],
                            },
                        }
                    ],
                    "aggregated_results": {
                        "submissions": [{"uuid": "test-submission-uuid", "result": 2.5}]
                    },
                },
            }
        ],
        "participants": [
            {
                "uuid": "test-participant-uuid",
                "model": "gpt-3.5-turbo",
                "type": "ConversableAgentParticipant",
                "role_description": "Test role description",
            }
        ],
    }


@pytest.fixture
def sample_session_file(sample_session_data):
    with NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
        json.dump(sample_session_data, temp_file)
    yield temp_file.name
    Path(temp_file.name).unlink()


def test_parse_session_json_with_dict(sample_session_data):
    tables = parse_session_json(sample_session_data)

    assert "participants" in tables
    assert "topics" in tables
    assert "submissions" in tables
    assert "votes" in tables

    assert isinstance(tables["participants"], pd.DataFrame)
    assert isinstance(tables["topics"], pd.DataFrame)
    assert isinstance(tables["submissions"], pd.DataFrame)
    assert isinstance(tables["votes"], pd.DataFrame)

    assert len(tables["participants"]) == 1
    assert len(tables["topics"]) == 1
    assert len(tables["submissions"]) == 1
    assert len(tables["votes"]) == 1

    assert tables["participants"].iloc[0]["uuid"] == "test-participant-uuid"
    assert tables["topics"].iloc[0]["uuid"] == "test-topic-uuid"
    assert tables["submissions"].iloc[0]["uuid"] == "test-submission-uuid"
    assert tables["votes"].iloc[0]["participant_uuid"] == "test-participant-uuid"

    assert tables["submissions"].iloc[0]["aggregated_result"] == pytest.approx(2.5)


def test_parse_session_json_with_file(sample_session_file):
    tables = parse_session_json(sample_session_file)

    assert "participants" in tables
    assert "topics" in tables
    assert "submissions" in tables
    assert "votes" in tables

    assert isinstance(tables["participants"], pd.DataFrame)
    assert isinstance(tables["topics"], pd.DataFrame)
    assert isinstance(tables["submissions"], pd.DataFrame)
    assert isinstance(tables["votes"], pd.DataFrame)

    assert len(tables["participants"]) == 1
    assert len(tables["topics"]) == 1
    assert len(tables["submissions"]) == 1
    assert len(tables["votes"]) == 1


def test_invalid_input():
    with pytest.raises(ValueError):
        parse_session_json(42)  # Invalid input type
