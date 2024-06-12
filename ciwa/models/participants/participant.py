# models/participants/participant.py

from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Dict, Any
from ciwa.models.identifiable import Identifiable


class Participant(Identifiable, ABC):
    """
    Abstract base class representing a participant in the system.

    This class provides the necessary interface for participants,
    whether human or automated agents (like LLM), to interact with topics
    and generate submissions.
    """

    def __init__(self) -> None:
        """
        Initializes a new Participant instance with a unique identifier.
        """
        super().__init__()

    @abstractmethod
    async def generate_submissions(
        self, topic: "Topic", num_submissions: int
    ) -> AsyncGenerator["Submission", None]:
        """
        An asynchronous generator method that yields submissions for a given topic.

        This method needs to be implemented by subclasses to define how submissions
        are generated based on the participant's logic and the characteristics of the topic.

        Args:
            topic (Topic): The topic for which submissions are to be generated.
            num_submissions (int): The number of submissions to generate.

        Yields:
            Submission: A submission created by the participant for the specified topic.

        Example:
            async for submission in participant.generate_submissions(topic, 5):
                process_submission(submission)
        """
        pass

    @abstractmethod
    async def create_submission(self, topic: "Topic") -> "Submission":
        """
        Creates a submission for the given topic.

        Args:
            topic (Topic): The topic for which the submission is created.

        Returns:
            Submission: The created submission.
        """
        pass

    @abstractmethod
    async def get_labeling_vote_response(
        self, submission: "Submission", vote_schema: Dict[str, Any], vote_prompt: str
    ) -> Dict:
        """
        Generates a labeling vote for a given submission.

        Args:
            submission (Submission): The submission for which the vote is cast.
            vote_schema (dict): The schema for the vote.
            vote_prompt (str): The prompt for the vote.

        Returns:
            dict: The vote response.
        """
        pass

    @abstractmethod
    async def get_comparative_vote_response(
        self,
        submissions: List["Submission"],
        vote_schema: Dict[str, Any],
        vote_prompt: str,
    ) -> Dict:
        """
        Generates a comparative vote for a list of submissions.

        Args:
            submissions (List[Submission]): The list of submissions to compare.
            vote_schema (dict): The schema for the vote.
            vote_prompt (str): The prompt for the vote.

        Returns:
            dict: The vote response.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent a Participant object's properties.

        Returns:
            dict: The JSON schema.
        """
        pass

    @abstractmethod
    def to_json(self) -> dict:
        """
        Returns a JSON representation of the Participant object.

        Returns:
            dict: A dictionary representing the participant object.
        """
        return {"uuid": self.uuid}

    def __str__(self) -> str:
        """
        Provides a string representation of the participant.

        Returns:
            str: A string that includes the participant's identifier.
        """
        return f"Participant ID: {self.uuid}"
