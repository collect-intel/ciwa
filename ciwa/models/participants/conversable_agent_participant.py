# models/participants/conversable_agent_participant.py

from typing import Any, Dict
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
import autogen
import logging
import os


class ConversableAgentParticipant(LLMAgentParticipant):
    def __init__(self, model: str, **kwargs) -> None:
        super().__init__(model, **kwargs)
        self.agent: "ConversableAgent" = self._init_agent(**kwargs)

    def _init_agent(self, **kwargs) -> "ConversableAgent":
        config_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "OAI_CONFIG_LIST.json"
            )
        )
        logging.info(f"Loading config from: {config_path}")
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found at path: {config_path}")

        config_list = self._load_config_list(config_path)

        agent_kwargs = {
            key: kwargs[key]
            for key in {"temperature", "timeout", "cache_seed"}
            if key in kwargs
        }

        return autogen.ConversableAgent(
            name="assistant",
            llm_config={"config_list": config_list, **agent_kwargs},
            human_input_mode="NEVER",
            code_execution_config=False,
        )

    def _load_config_list(self, config_path: str) -> list:
        filter_dict = {
            "response_format": [{"type": "json_object"}],
            "model": self.model,
        }
        config_list = autogen.config_list_from_json(env_or_file=config_path)
        config_list = autogen.filter_config(config_list, filter_dict)
        if len(config_list) != 1:
            logging.error(
                f"Expected exactly one config for model {self.model}, but found {len(config_list)}"
            )
            raise ValueError(
                f"Expected exactly one config for model {self.model}, but found {len(config_list)}"
            )
        return config_list

    async def send_prompt(self, prompt: str, response_schema: Dict[str, Any]) -> str:
        prompt += f"\n{self.get_respond_with_json(response_schema)}"
        reply = await self.agent.a_generate_reply(
            messages=[{"content": prompt, "role": "user"}]
        )
        return reply
