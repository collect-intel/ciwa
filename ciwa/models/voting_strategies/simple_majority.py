# filename: ciwa/models/voting_strategies/simple_majority.py

from typing import List
from ciwa.models.voting_strategies.voting_strategy import (
    IndependentVotingStrategy,
    VoteType,
)
from ciwa.models.votes.independent_vote import BinaryVote


class SimpleMajority(IndependentVotingStrategy[BinaryVote]):
    """
    Concrete VotingStrategy class implementing a simple majority rule,
    where the outcome is determined by the majority of yes (True) or no (False) votes.
    """

    def process_votes(self, votes: List[BinaryVote]) -> bool:
        """
        Processes a list of binary votes to determine the majority vote.

        Args:
            votes (List[BinaryVote]): The list of binary votes to process.

        Returns:
            bool: True if the majority of votes are True (yes), False otherwise.
        """
        yes_count = sum(vote.get_value() for vote in votes if vote.get_value() is True)
        no_count = len(votes) - yes_count
        return yes_count > no_count

    @staticmethod
    def get_vote_type() -> str:
        return "binary_vote"

    def __str__(self) -> str:
        """
        Provides a string representation of the voting strategy.

        Returns:
            str: A string describing the SimpleMajority voting strategy.
        """
        return "Simple Majority Voting Strategy"
