# models/participants/participant_factory.py

import logging
from typing import Any
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant
from ciwa.models.participants.conversable_agent_participant import (
    ConversableAgentParticipant,
)


class ParticipantFactory:
    """
    Factory class for creating participants.
    """

    @staticmethod
    def create_participant(type: str, **kwargs) -> "Participant":
        """
        Factory method to create a participant of the specified type.

        Args:
            type (str): Type of participant to create.
                        Currently supports 'LLMAgentParticipant' and 'ConversableAgentParticipant'.
            kwargs (Any): Additional keyword arguments necessary for initializing participants.

        Returns:
            Participant: An instance of Participant.

        Raises:
            ValueError: If the type is not supported.
        """
        if type == "LLMAgentParticipant":
            return LLMAgentParticipant(**kwargs)
        elif type == "ConversableAgentParticipant":
            model = kwargs.pop("model")
            prompt_template = kwargs.pop("prompt_template")
            if not model or not prompt_template:
                logging.error(
                    "Model or prompt_template not provided for ConversableAgentParticipant creation."
                )
                raise ValueError(
                    "Model and prompt template must be provided for ConversableAgentParticipant."
                )
            return ConversableAgentParticipant(
                model=model, prompt_template=prompt_template, **kwargs
            )
        else:
            logging.error(f"Unsupported participant type: {type}")
            raise ValueError(f"Participant type {type} is not supported.")
