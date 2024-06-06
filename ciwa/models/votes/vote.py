# filename: ciwa/models/votes/vote.py
import datetime
from abc import ABC, abstractmethod
from typing import Type
import re


class Vote(ABC):
    """
    Abstract base class representing a general vote in the system.

    This class provides the framework for defining various types of votes,
    each potentially with different voting mechanics (e.g., binary, ranked, quadratic).
    Subclasses must implement the get_value method, which should return
    the computed value of the vote based on its specific logic.

    Attributes:
        participant (Participant): The participant who cast the vote.
        timestamp (datetime.datetime): Timestamp when the vote was cast.
    """

    def __init__(
        self,
        participant: "Participant",
    ) -> None:
        """
        Initializes a new Vote instance with a participant and timestamp.

        Args:
            participant (Participant): The participant casting the vote.
            timestamp (datetime.datetime, optional): The time when the vote is recorded.
                Defaults to the current datetime if not provided.
        """
        self.participant = participant
        self.created_at = datetime.datetime.now()
        self.type = self._get_vote_type()

    def _get_vote_type(self) -> str:
        """
        Returns the snake_case string of the concrete class name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    @abstractmethod
    def get_value(self):
        """
        Computes and returns the value of the vote based on the voting strategy.

        Returns:
            The computed value of the vote. The type and nature of the value depend on the specific voting strategy.
        """
        pass

    def __str__(self) -> str:
        """
        Provides a string representation of the vote, which can be used for logging or debugging.

        Returns:
            str: A string describing the vote, including the participant's identifier and the computed value.
        """
        return f"Vote ({self.type}) by {self.participant.uuid} at {self.created_at}: {self.get_value()}"
