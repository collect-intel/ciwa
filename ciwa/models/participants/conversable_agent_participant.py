# models/participants/conversable_agent_participant.py

"""
This module contains the ConversableAgentParticipant class, which represents a participant
that interacts with a ConversableAgent in the CIWA system.
"""

import logging
import os
from typing import Any, Dict
import autogen
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant


class ConversableAgentParticipant(LLMAgentParticipant):
    """
    Represents a participant that interacts with a ConversableAgent in the CIWA system.
    """

    def __init__(self, model: str, **kwargs) -> None:
        """
        Initializes a new instance of ConversableAgentParticipant.

        Args:
            model (str): The model to use for the ConversableAgent.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(model, **kwargs)
        self.agent: "ConversableAgent" = self._init_agent(**kwargs)

    def _init_agent(self, **kwargs) -> "ConversableAgent":
        """
        Initializes the ConversableAgent with the provided configuration.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            ConversableAgent: The initialized ConversableAgent.
        """
        config_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "OAI_CONFIG_LIST.json"
            )
        )
        logging.info("Loading config from: %s", config_path)
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found at path: {config_path}")

        config_list = self._load_config_list(config_path)

        agent_kwargs = {
            key: kwargs[key]
            for key in ["temperature", "timeout", "cache_seed"]
            if key in kwargs
        }

        logging.info(
            "Creating ConversableAgent with config: %s and kwargs: %s",
            config_list,
            agent_kwargs,
        )

        return autogen.ConversableAgent(
            name="assistant",
            llm_config={"config_list": config_list, **agent_kwargs},
            human_input_mode="NEVER",
            code_execution_config=False,
        )

    def _load_config_list(self, config_path: str) -> list:
        """
        Loads the configuration list from the specified path.

        Args:
            config_path (str): The path to the configuration file.

        Returns:
            list: The loaded configuration list.
        """
        filter_dict = {
            "model": self.model,
        }
        config_list = autogen.config_list_from_json(env_or_file=config_path)
        config_list = autogen.filter_config(config_list, filter_dict)
        if len(config_list) != 1:
            logging.error(
                "Expected exactly one config for model %s, but found %d",
                self.model,
                len(config_list),
            )
            raise ValueError(
                f"Expected exactly one config for model {self.model}, but found {len(config_list)}"
            )
        return config_list

    async def send_prompt(self, prompt: str, response_schema: Dict[str, Any]) -> str:
        """
        Sends a prompt to the ConversableAgent and returns the response.

        Args:
            prompt (str): The prompt to send.
            response_schema (Dict[str, Any]): The schema to validate the response against.

        Returns:
            str: The response from the ConversableAgent.
        """
        prompt += f"\n{self.get_respond_with_json(response_schema)}"
        reply = await self.agent.a_generate_reply(
            messages=[{"content": prompt, "role": "user"}]
        )
        return reply
