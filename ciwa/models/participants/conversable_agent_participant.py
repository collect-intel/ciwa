# models/participants/conversable_agent_participant.py

"""
This module contains the ConversableAgentParticipant class, which represents a participant
that interacts with a ConversableAgent in the CIWA system.
"""

import logging
import os
from typing import Any, Dict, List
import re
import autogen
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
import ciwa.utils.json_utils as json_utils


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
        config_list = self._add_model_specific_config(config_list)

        agent_kwargs = {
            key: kwargs[key]
            for key in ["temperature", "timeout", "cache_seed"]
            if key in kwargs
        }

        logging.info(
            "Creating ConversableAgent %s with config: %s and kwargs: %s",
            self.uuid,
            config_list,
            agent_kwargs,
        )

        return autogen.ConversableAgent(
            name="assistant",
            llm_config={"config_list": config_list, **agent_kwargs},
            human_input_mode="NEVER",
            code_execution_config=False,
        )

    def _add_model_specific_config(
        self, config_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Adds model-specific configuration to the provided configuration.

        Args:
            config_list (List[Dict[str, Any]]): The configuration list to update.

        Returns:
            List[Dict[str, Any]]: The updated configuration list.
        """
        if "gemini" in self.model:
            # Default safety settings.
            default_safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
            for config in config_list:
                # Overwrite default settings with those provided in config, if any.
                if "safety_settings" in config:
                    config_safety_dict = {
                        setting["category"]: setting["threshold"]
                        for setting in config["safety_settings"]
                    }
                    updated_safety_settings = [
                        {
                            "category": category,
                            "threshold": config_safety_dict.get(category, threshold),
                        }
                        for category, threshold in default_safety_settings.items()
                    ]
                else:
                    # If no overrides, convert default settings to list format.
                    updated_safety_settings = [
                        {"category": k, "threshold": v}
                        for k, v in default_safety_settings.items()
                    ]

                config["safety_settings"] = updated_safety_settings

        return config_list

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

    async def _send_prompt(self, prompt: str) -> str:
        """
        Sends a prompt to the ConversableAgent and returns the response.

        Args:
            prompt (str): The prompt to send.

        Returns:
            str: The response from the ConversableAgent.
        """
        messages = [{"content": prompt, "role": "user"}]
        reply = await self.agent.a_generate_reply(messages=messages)
        return self._get_model_specific_response(reply)

    def _get_model_specific_response(self, response: any) -> str:
        """
        Extracts the model-specific response from the response dictionary.

        Args:
            response (Dict[str, Any]): The response dictionary.

        Returns:
            str: The model-specific response.
        """
        if "claude" in self.model or "gemini" in self.model or "mistral" in self.model:
            response = response["content"]
            if not response.startswith("{"):
                logging.info(
                    "LLM response from %s is not json only. Extracting json from response:\n%s",
                    self.uuid,
                    response,
                )
                response = json_utils.extract_json(text=response)
        return response
