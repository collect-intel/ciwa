# filename: ciwa/models/participants/conversable_agent_participant.py

from typing import Any, Dict, List
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
import autogen
import logging
import os
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ConversableAgentParticipant(LLMAgentParticipant):
    def __init__(self, model: str, prompt_template: str, **kwargs) -> None:
        super().__init__(model, prompt_template, **kwargs)
        self.agent: "ConversableAgent" = self._init_agent(**kwargs)

    def _init_agent(self, **kwargs) -> "ConversableAgent":
        # Navigate up two directories from the current file's directory
        config_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "OAI_CONFIG_LIST.json"
            )
        )

        # Print the constructed path for debugging
        logging.info(f"Loading config from: {config_path}")
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found at path: {config_path}")

        config_list = autogen.config_list_from_json(env_or_file=config_path)

        AGENT_ARGS = {"temperature", "timeout"}
        agent_kwargs = {key: kwargs[key] for key in AGENT_ARGS if key in kwargs}

        agent = autogen.ConversableAgent(
            name="assistant",
            llm_config={"config_list": config_list, **agent_kwargs},
        )
        return agent

    def _load_config_list(self) -> None:
        filter_dict = {"tags": [model, "json"]}
        config_list = autogen.filter_config(config_list, filter_dict)
        assert len(config_list) == 1
        return config_list

    async def send_prompt(self, prompt: str, response_schema: Dict[str, Any]) -> str:
        prompt = prompt
        prompt += f"\n{self.get_respond_with_json(response_schema)}"
        reply = self.agent.generate_reply(
            messages=[{"content": prompt, "role": "user"}]
        )
        return reply
