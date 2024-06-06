# filename: ciwa/models/votes/independent_vote.py

from abc import ABC, abstractmethod
from ciwa.models.votes.vote import Vote
from typing import Any


class IndependentVote(Vote, ABC):
    """
    Abstract class representing a vote on an individual Submission independent from evaluating any other Submissions.
    """

    def __init__(self, participant: "Participant", vote_value: Any) -> None:
        super().__init__(participant)
        self.vote_value = vote_value

    def get_value(self) -> Any:
        return self.vote_value


class BinaryVote(IndependentVote):
    """
    Concrete implementation of a binary vote, where the vote is either yes (True) or no (False).

    Attributes:
        vote_value (bool): The boolean value representing the vote, True for 'yes' and False for 'no'.
    """

    def __init__(self, participant: "Participant", vote_value: bool) -> None:
        """
        Initializes a new instance of BinaryVote with the participant and a boolean value.

        Args:
            participant (Participant): The participant casting the vote.
            vote_value (bool): The boolean value of the vote (True for yes, False for no).
        """
        super().__init__(participant)
        self.vote_value = vote_value

    def get_value(self) -> bool:
        """
        Returns the boolean value of the vote.

        Returns:
            bool: The vote value, True for 'yes' and False for 'no'.
        """
        return self.vote_value

    def __str__(self) -> str:
        """
        Provides a string representation of the binary vote, indicating the participant and vote value.

        Returns:
            str: A string describing the vote, showing 'yes' for True and 'no' for False.
        """
        vote_description = "yes" if self.vote_value else "no"
        return f"Binary Vote by {self.participant.uuid} at {self.created_at}: {vote_description}"
