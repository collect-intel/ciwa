import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ciwa.models.participants.conversable_agent_participant import (
    ConversableAgentParticipant,
)
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
from ciwa.models.submission import Submission
from ciwa.tests.utils.model_utils import (
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


@pytest.fixture
def conversable_agent_participant(mock_file_operations):
    return ConversableAgentParticipant(model="gpt-3.5-turbo")


@pytest.fixture
def topic():
    return create_topic(title="Test Topic", description="A test topic")


@pytest.fixture
def mock_prompt_loader():
    with patch(
        "ciwa.models.participants.llm_agent_participant.prompt_loader.get_prompts"
    ) as mock:
        mock.return_value = {
            "system_message": "Welcome to the {process_name}. This is a {process_description}.",
            "submission_prompt": "Please generate a submission for this topic: {topic_title}\nDescription: {topic_description}",
            "invalid_json_response": "Invalid JSON response. Please try again.",
            "respond_with_json": "Your response must be in JSON format. Please respond only with valid JSON that would conform to the schema below. Make sure to respond with valid JSON, and not with another JSON schema.\n{schema}",
        }
        yield mock


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
