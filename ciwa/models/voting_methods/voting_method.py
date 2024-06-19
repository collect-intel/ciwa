# filename: ciwa/voting_methods/voting_method.py

from abc import ABC, abstractmethod
from typing import List, TypeVar, Any, Dict
from ciwa.utils import prompt_loader
from ciwa.models.submission import Submission
from ciwa.models.voting_results import VotingResults


class VotingMethod(ABC):
    """
    Abstract base class for voting voting methods.
    """

    def __init__(self) -> None:
        self.vote_prompt = prompt_loader.get_prompts(self.__class__)["vote_prompt"]

    @property
    def type(self) -> str:
        """
        Return the class name as a string.
        """
        return self.__class__.__name__

    @abstractmethod
    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Processes a VotingResults object to get an aggregated result.

        Args:
            voting_results (VotingResults): An object holding the voting results.
            submission_ids (List[str]): List of submission.uuid's that were available for voting.
                Allows aggregate results to return empty/none values for submissions that received no votes.
        Returns:
            Any: The result of the vote processing, specific to the voting_method.
        """
        pass

    @abstractmethod
    def get_vote_schema(self, **kwargs) -> Dict[str, Any]:
        """
        Returns the JSON schema for the vote data.
        """
        pass

    @abstractmethod
    def get_vote_prompt(self, **kwargs) -> str:
        """
        Returns a prompt for the vote.
        """
        pass

    @staticmethod
    @abstractmethod
    def is_label() -> bool:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Voting Method"


class LabelVotingMethod(VotingMethod, ABC):
    """
    Abstract VotingMethod class implementing a label voting rule,
    where votes are given on Submissions independently without compare to other Submissions,
    effectively applying a label to each Submission.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def is_label() -> bool:
        return True

    @abstractmethod
    def get_vote_schema(self) -> Dict[str, Any]:
        pass

    def get_vote_prompt(self, submission: "Submission", **kwargs) -> str:
        if isinstance(submission, Submission):
            return self.vote_prompt.format(
                submission_content=submission.content, **kwargs
            )
        else:
            raise TypeError(
                "get_vote_prompt() requires a single submission for label voting methods."
            )


class CompareVotingMethod(VotingMethod, ABC):
    """
    Abstract VotingMethod class implementing a compare voting rule,
    where votes are given on a set of Submissions by comparing them to each other.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def is_label() -> bool:
        return False

    @abstractmethod
    def get_vote_schema(self, num_submissions: int) -> Dict[str, Any]:
        pass

    def get_vote_prompt(self, submissions: List["Submission"], **kwargs) -> str:
        if isinstance(submissions, list):
            submissions_contents_str = ""
            for i, submission in enumerate(submissions):
                submissions_contents_str += (
                    f"Submission {i + 1}:\n{submission.content}\n\n"
                )
            return self.vote_prompt.format(
                submissions_contents=submissions_contents_str, **kwargs
            )
        else:
            raise TypeError(
                "get_vote_prompt() requires a list of submissions for compare voting methods."
            )
