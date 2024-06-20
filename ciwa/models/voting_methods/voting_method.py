# models/voting_methods/voting_method.py
"""
This module contains abstract base classes for different voting methods
used in the CIWA application.
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from ciwa.utils import prompt_loader
from ciwa.models.submission import Submission
from ciwa.models.voting_results import VotingResults


class VotingMethod(ABC):
    """
    Abstract base class for voting methods.
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
            submission_ids (List[str]): List of submission.uuid's that were available
                                        for voting. Allows aggregate results to return
                                        empty/none values for submissions that received
                                        no votes.
        Returns:
            Any: The result of the vote processing, specific to the voting_method.
        """

    @abstractmethod
    def get_vote_schema(self, **kwargs) -> Dict[str, Any]:
        """
        Returns the JSON schema for the vote data.
        """

    @abstractmethod
    def get_vote_prompt(self, **kwargs) -> str:
        """
        Returns a prompt for the vote.
        """

    @staticmethod
    @abstractmethod
    def is_label() -> bool:
        """
        Returns True if the voting method is a label voting method.
        """

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Voting Method"


class LabelVotingMethod(VotingMethod, ABC):
    """
    Abstract VotingMethod class implementing a label voting rule,
    where votes are given on Submissions independently without
    comparing to other Submissions, effectively applying a label
    to each Submission.
    """

    @staticmethod
    def is_label() -> bool:
        return True

    def get_vote_prompt(self, submission: Submission, **kwargs) -> str:
        """
        Returns a prompt to give the Participants to decide their vote.
        """

        if isinstance(submission, Submission):
            return self.vote_prompt.format(
                submission_content=submission.content, **kwargs
            )
        raise TypeError(
            "get_vote_prompt() requires a single submission for label voting methods."
        )


class CompareVotingMethod(VotingMethod, ABC):
    """
    Abstract VotingMethod class implementing a compare voting rule,
    where votes are given on a set of Submissions by comparing them to each other.
    """

    @staticmethod
    def is_label() -> bool:
        return False

    def get_vote_prompt(self, submissions: List[Submission], **kwargs) -> str:
        """
        Returns a prompt to give the Participants to decide their vote.
        """
        if isinstance(submissions, list):
            submissions_contents_str = "".join(
                f"Submission {i + 1}:\n{submission.content}\n\n"
                for i, submission in enumerate(submissions)
            )
            return self.vote_prompt.format(
                submissions_contents=submissions_contents_str, **kwargs
            )
        raise TypeError(
            "get_vote_prompt() requires a list of submissions for compare voting methods."
        )
