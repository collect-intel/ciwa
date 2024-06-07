# filename: ciwa/strategies/voting_strategies/voting_strategy.py

from abc import ABC, abstractmethod
from typing import List, TypeVar, Any, Dict


class VotingStrategy(ABC):
    """
    Abstract base class for voting strategies.
    """

    @abstractmethod
    def process_votes(self, participant_votes_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a list of participant vote responses to get an aggregated result.

        Args:
            participant_votes_data (Dict[str, Any]): A dictionary of participant vote responses.
        Returns:
            Any: The result of the vote processing, specific to the strategy.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_vote_type() -> str:
        """
        Returns the type of vote used by this strategy.

        Returns:
            str: The vote type.
        """
        pass

    @abstractmethod
    def get_vote_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON schema for the vote data.
        """
        pass

    @staticmethod
    @abstractmethod
    def is_labeling(self) -> bool:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Voting Strategy"


class LabelingStrategy(VotingStrategy, ABC):
    """
    Abstract VotingStrategy class implementing an labeling voting rule,
    where votes are given on Submissions independently without comparison to other Submissions,
    effectively applying a label to each Submission.
    """

    def is_labeling(self) -> bool:
        return True


class ComparativeVotingStrategy(VotingStrategy, ABC):
    """
    Abstract VotingStrategy class implementing a comparative voting rule,
    where votes are given on a set of Submissions by comparing them to each other.
    """

    def is_labeling(self) -> bool:
        return False
