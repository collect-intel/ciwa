import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
from ciwa.models.submission import Submission
from ciwa.tests.utils.model_utils import (
    create_session,
    create_topic,
    create_submission,
    create_participant,
)


@pytest.fixture
def topic():
    session = create_session(name="Test Session", description="A test session")
    return create_topic(session=session, title="Test Topic", description="A test topic")


def mock_get_prompts(cls: type, yaml_file: str = "dummy_file.yaml") -> dict:
    prompts = {
        "LLMAgentParticipant": {
            "system_message": "Welcome to the {process_name}. This is a {process_description}.\n{role_description}\n{current_session_message}",
            "submission_prompt": "Please generate a submission for this topic: {topic_title}\nDescription: {topic_description}",
            "invalid_json_response": "Invalid JSON response. Please try again.",
            "respond_with_json": "Your response must be in JSON: {schema}",
            "current_session_message": "Current session is {session_name}: {session_description}",
        },
        "RankingCompare": {
            "vote_prompt": "Please rank the following submissions from your most preferred to least preferred:\n\n{submissions_contents}\n\nReturn the rankings as a list of submission numbers, where the first item is your top preference and the last item is your least preferred."
        },
    }

    class_name = cls.__name__
    return prompts.get(class_name, {})


@pytest.fixture
def mock_prompt_loader():
    with patch("ciwa.utils.prompt_loader.get_prompts", side_effect=mock_get_prompts):
        yield


@pytest.fixture
def llm_agent_participant(mock_prompt_loader):
    process = create_session().process
    return LLMAgentParticipant(process=process, model="gpt-3.5-turbo")


@pytest.mark.asyncio
async def test_generate_submissions(llm_agent_participant, topic, mock_prompt_loader):
    num_submissions = 3
    submissions = [
        submission
        async for submission in llm_agent_participant.generate_submissions(
            topic, num_submissions
        )
    ]
    assert len(submissions) == num_submissions
    assert all(isinstance(submission, Submission) for submission in submissions)


@pytest.mark.asyncio
async def test_create_submission(llm_agent_participant, topic, mock_prompt_loader):
    with patch.object(
        llm_agent_participant,
        "send_prompt_with_retries",
        return_value={"submission": {"content": "Test content"}},
    ):
        submission = await llm_agent_participant.create_submission(topic)
        assert submission is not None
        assert submission.content == "Test content"


@pytest.mark.asyncio
async def test_get_submission_response(llm_agent_participant, mock_prompt_loader):
    schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
        "additionalProperties": False,
    }

    with patch.object(
        llm_agent_participant,
        "send_prompt_with_retries",
        return_value={"submission": {"content": "Valid content"}},
    ):
        response = await llm_agent_participant._get_submission_response(
            prompt="Test prompt",
            schema=schema,
            validator=lambda x: True,
            invalid_message="Invalid submission",
        )
        assert response == {"submission": {"content": "Valid content"}}


@pytest.mark.asyncio
async def test_send_prompt_with_retries(llm_agent_participant, mock_prompt_loader):
    schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
        "additionalProperties": False,
    }

    async def mock_send_prompt(prompt, response_schema):
        return {"submission": {"content": "Test content"}}

    with patch.object(llm_agent_participant, "send_prompt", new=mock_send_prompt):
        response = await llm_agent_participant.send_prompt_with_retries(
            prompt="Test prompt",
            response_schema=schema,
            validation_steps=[(lambda x: True, "Invalid response")],
        )
        assert response == {"submission": {"content": "Test content"}}


@pytest.mark.asyncio
async def test_get_vote_response(llm_agent_participant, mock_prompt_loader):
    schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
        "additionalProperties": False,
    }

    with patch.object(
        llm_agent_participant,
        "send_prompt_with_retries",
        return_value={"submission": {"content": "Valid content"}},
    ):
        response = await llm_agent_participant._get_vote_response(
            prompt="Test prompt", schema=schema
        )
        assert response == {"submission": {"content": "Valid content"}}


@pytest.mark.asyncio
async def test_get_label_vote_response(
    llm_agent_participant, topic, mock_prompt_loader
):
    submission = create_submission(topic=topic, content="Test content")
    schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
        "additionalProperties": False,
    }

    with patch.object(
        llm_agent_participant, "_get_vote_response", return_value={"vote": "yes"}
    ):
        response = await llm_agent_participant.get_label_vote_response(
            submission=submission, vote_schema=schema, vote_prompt="Vote prompt"
        )
        assert response == {"vote": "yes"}


@pytest.mark.asyncio
async def test_get_compare_vote_response(
    llm_agent_participant, topic, mock_prompt_loader
):
    submissions = [
        create_submission(topic=topic, content=f"Test content {i}") for i in range(3)
    ]
    schema = {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
        "additionalProperties": False,
    }

    with patch.object(
        llm_agent_participant, "_get_vote_response", return_value={"vote": [1, 2, 3]}
    ):
        response = await llm_agent_participant.get_compare_vote_response(
            submissions=submissions, vote_schema=schema, vote_prompt="Vote prompt"
        )
        assert response == {"vote": [1, 2, 3]}
