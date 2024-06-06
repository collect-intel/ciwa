# filename: ciwa/strategies/voting_strategies/voting_strategy.py

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Any

VoteType = TypeVar("VoteType", bound="Vote")


class VotingStrategy(ABC, Generic[VoteType]):
    """
    Abstract base class for voting strategies.
    """

    @abstractmethod
    def process_votes(self, votes: List[VoteType]) -> Any:
        """
        Processes a list of votes and determines the result based on the specific strategy.

        Args:
            votes (List[VoteType]): The list of votes to process. Each item is an instance of a subclass of Vote.

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
    def is_independent(self) -> bool:
        pass


class IndependentVotingStrategy(VotingStrategy[VoteType], ABC):
    """
    Abstract VotingStrategy class implementing an independent voting rule,
    where votes are given on Submissions independently without comparison to other Submissions.
    """

    def is_independent(self) -> bool:
        return True


class ComparativeVotingStrategy(VotingStrategy[VoteType], ABC):
    """
    Abstract VotingStrategy class implementing a comparative voting rule,
    where votes are given on a set of Submissions by comparing them to each other.
    """

    def is_independent(self) -> bool:
        return False
