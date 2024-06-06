# filename: ciwa/models/participants/participant_factory.py

import sys
from typing import Dict, Any
import logging
from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


from ciwa.models.participants.llm_agent_participant import LLMAgentParticipant


class ParticipantFactory:
    """
    Factory class for creating participants.
    """

    @staticmethod
    def create_participant(type: str, **kwargs) -> "Participant":
        """
        Factory method to create a participant of the specified type.

        Args:
            type: Type of participant to create. Currently supports only 'LLMAgentParticipant'.
            kwargs: Additional keyword arguments necessary for initializing participants.

        Returns:
            An instance of Participant.

        Raises:
            ValueError: If the participant_type is not supported.
        """
        if type == "LLMAgentParticipant":
            model = kwargs.get("model")
            prompt_template = kwargs.get("prompt_template")
            if not model or not prompt_template:
                logging.error(
                    "Model or prompt_template not provided for LLMAgentParticipant creation."
                )
                raise ValueError(
                    "Model and prompt template must be provided for LLMAgentParticipant."
                )
            return LLMAgentParticipant(model=model, prompt_template=prompt_template)
        else:
            logging.error(f"Unsupported participant type: {type}")
            raise ValueError(f"Participant type {type} is not supported.")
