import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ciwa.models.participants.conversable_agent_participant import (
    ConversableAgentParticipant,
)
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
from ciwa.models.submission import Submission
from ciwa.tests.utils.model_utils import (
    create_process,
    create_session,
    create_topic,
    create_submission,
    create_participant,
)


@pytest.fixture
def mock_openai():
    with patch("autogen.oai.client.OpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        yield mock_openai


@pytest.fixture
def mock_file_operations(mock_openai):
    with patch("os.path.isfile", return_value=True), patch(
        "ciwa.models.participants.conversable_agent_participant.autogen.config_list_from_json",
        return_value=[{"config": "test"}],
    ), patch(
        "ciwa.models.participants.conversable_agent_participant.autogen.filter_config",
        return_value=[{"config": "test"}],
    ):
        yield


def mock_get_prompts(cls: type, yaml_file: str = "dummy_file.yaml") -> dict:
    prompts = {
        "LLMAgentParticipant": {
            "system_message": "Welcome to the {process_name}. This is a {process_description}.\n{role_description}\n{current_session_message}",
            "submission_prompt": "Please generate a submission for this topic: {topic_title}\nDescription: {topic_description}",
            "invalid_json_response": "Invalid JSON response. Please try again.",
            "respond_with_json": "Your response must be in JSON: {schema}",
            "current_session_message": "Current session is {session_name}: {session_description}",
        },
        "ConversableAgentParticipant": {
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
def conversable_agent_participant(mock_file_operations, mock_prompt_loader):
    process = create_session().process
    return ConversableAgentParticipant(process=process, model="gpt-3.5-turbo")


@pytest.fixture
def topic():
    return create_topic(title="Test Topic", description="A test topic")


def test_initialization(conversable_agent_participant):
    assert isinstance(conversable_agent_participant, LLMAgentParticipant)
    assert conversable_agent_participant.model == "gpt-3.5-turbo"


@patch(
    "ciwa.models.participants.conversable_agent_participant.os.path.isfile",
    return_value=True,
)
@patch(
    "ciwa.models.participants.conversable_agent_participant.autogen.config_list_from_json"
)
@patch("ciwa.models.participants.conversable_agent_participant.autogen.filter_config")
@patch.dict("os.environ", {"OPENAI_API_KEY": "test_api_key"})
def test_init_agent(
    mock_filter_config,
    mock_config_list_from_json,
    mock_isfile,
    conversable_agent_participant,
):

    mock_config_list_from_json.return_value = [{"config": "test"}]
    mock_filter_config.return_value = [{"config": "test"}]
    agent = conversable_agent_participant._init_agent(temperature=0.7, timeout=30)
    assert agent is not None
    mock_config_list_from_json.assert_called_once()
    mock_filter_config.assert_called_once()


def test_load_config_list(conversable_agent_participant):
    config_list = conversable_agent_participant._load_config_list(
        "/dummy/path/to/config"
    )
    assert config_list == [{"config": "test"}]


@pytest.mark.asyncio
async def test_send_prompt(conversable_agent_participant):
    with patch.object(
        conversable_agent_participant.agent, "a_generate_reply", new_callable=AsyncMock
    ) as mock_generate_reply:
        mock_generate_reply.return_value = "Test reply"
        schema = {
            "type": "object",
            "properties": {"content": {"type": "string"}},
            "required": ["content"],
            "additionalProperties": False,
        }

        response = await conversable_agent_participant.send_prompt(
            "Test prompt", schema
        )
        assert response == "Test reply"
        mock_generate_reply.assert_called_once()


@pytest.mark.asyncio
async def test_create_submission(
    conversable_agent_participant, topic, mock_prompt_loader
):
    with patch.object(
        conversable_agent_participant,
        "send_prompt_with_retries",
        return_value={"submission": {"content": "Test content"}},
    ):
        submission = await conversable_agent_participant.create_submission(topic)
        assert submission is not None
        assert submission.content == "Test content"
