# models/participants/participant_factory.py

"""
Factory class for creating participants.
"""

import logging
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
            if not model:
                logging.error(
                    "Model not provided for ConversableAgentParticipant creation."
                )
                raise ValueError(
                    "Model must be provided for ConversableAgentParticipant."
                )
            return ConversableAgentParticipant(model=model, **kwargs)
        else:
            logging.error(f"Unsupported participant type: {type}")
            raise ValueError(f"Participant type {type} is not supported.")
