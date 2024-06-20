# models/voting_manager.py

"""
This module defines the VotingManager classes for managing and processing votes on topics.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Type, Dict, Any
import jsonschema
from ciwa.models.voting_methods.voting_method_registry import get_voting_method
from ciwa.models.voting_results import LabelVotingResults, CompareVotingResults


class VotingManager(ABC):
    """
    Abstract base class for managing the voting process for a given topic using a
    specified voting method.

    Attributes:
        voting_method (VotingMethod): The voting method to use for this topic.
        submissions_needing_votes (asyncio.Queue["Submission"]): Queue of submissions needing votes.
        results (VotingResults): Instance to hold and manage voting results.
        schema (Dict[str, Any]): The JSON schema for the vote data.
        submission_ids (List[str]): List of submission UUIDs that were made available for voting.
    """

    def __init__(
        self, voting_method_class: Type["VotingMethod"], topic: "Topic", **kwargs
    ) -> None:
        self.topic = topic
        self.voting_method: "VotingMethod" = voting_method_class(**kwargs)
        self.submissions_needing_votes: asyncio.Queue["Submission"] = asyncio.Queue()
        self.submission_ids: List[str] = []
        self.results: "VotingResults" = self.initialize_results()
        logging.info(
            "VotingManager initialized with voting_method: %s",
            self.voting_method.__class__.__name__,
        )

    @abstractmethod
    def initialize_results(self) -> "VotingResults":
        """
        Initialize the appropriate VotingResults instance.
        """

    def add_submission(self, submission: "Submission") -> None:
        """
        Add a submission to the queue of submissions needing votes.

        Args:
            submission ("Submission"): The submission to add.
        """
        self.submissions_needing_votes.put_nowait(submission)
        self.submission_ids.append(submission.uuid)

    @abstractmethod
    async def collect_votes(self, participants: List["Participant"]) -> None:
        """
        Collect votes from participants for the submissions.

        Args:
            participants (List[Participant]): List of participants to collect votes from.
        """

    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """
        Get the results of the voting process.

        Returns:
            Dict[str, Any]: The voting results.
        """


class LabelVotingManager(VotingManager):
    """
    Manager for collecting and processing label votes for a topic.
    """

    def __init__(
        self, voting_method_class: Type["VotingMethod"], topic: "Topic", **kwargs
    ) -> None:
        super().__init__(voting_method_class, topic, **kwargs)
        self.schema = self.voting_method.get_vote_schema()
        self.is_label = True

    def initialize_results(self) -> "VotingResults":
        return LabelVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            "Collecting label votes for submissions on topic %s from participants.",
            self.topic.uuid,
        )
        while not self.submissions_needing_votes.empty():
            submission = await self.submissions_needing_votes.get()
            vote_start_time = time.time()
            tasks = [
                asyncio.create_task(self.collect_label_vote(participant, submission))
                for participant in participants
            ]
            await asyncio.gather(*tasks)
            logging.info(
                "TIMING: Label votes collected for submission %s in %.2f seconds",
                submission.uuid,
                time.time() - vote_start_time,
            )

    async def collect_label_vote(
        self, participant: "Participant", submission: "Submission"
    ) -> None:
        """
        Collect a label vote from a participant for the given submission.
        """
        vote_json = await participant.get_label_vote_response(
            submission=submission,
            vote_schema=self.schema,
            vote_prompt=self.voting_method.get_vote_prompt(submission),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, {submission.uuid: vote_json})
        except jsonschema.ValidationError as e:
            logging.error("Invalid vote data: %s", e.message)

    def get_results(self) -> Dict[str, Any]:
        logging.info("Processing votes for topic %s.", self.topic.uuid)
        self.results.process_votes(self.voting_method, self.submission_ids)
        return self.results.to_json()


class CompareVotingManager(VotingManager):
    """
    Manager for collecting and processing compare votes for a topic.
    """

    def __init__(
        self, voting_method_class: Type["VotingMethod"], topic: "Topic", **kwargs
    ) -> None:
        super().__init__(voting_method_class, topic, **kwargs)
        self.schema = None
        self.is_label = False

    def initialize_results(self) -> "VotingResults":
        return CompareVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            "Collecting compare votes for submissions on topic %s from participants.",
            self.topic.uuid,
        )
        submissions = await self.get_all_submissions()
        tasks = [
            asyncio.create_task(self.collect_compare_vote(participant, submissions))
            for participant in participants
        ]
        await asyncio.gather(*tasks)

    async def collect_compare_vote(
        self, participant: "Participant", submissions: List["Submission"]
    ) -> None:
        """
        Collect a compare vote from a participant for the given submissions.
        """
        vote_json = await participant.get_compare_vote_response(
            submissions=submissions,
            vote_schema=self.schema,
            vote_prompt=self.voting_method.get_vote_prompt(submissions),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, vote_json)
            logging.info(
                "Compare vote for topic %s from participant %s added to results.",
                self.topic.uuid,
                participant.uuid,
            )
        except jsonschema.ValidationError as e:
            logging.error("Invalid vote data: %s", e.message)

    async def get_all_submissions(self) -> List["Submission"]:
        """
        Get all submissions needing votes from the queue.
        """
        submissions = []
        while not self.submissions_needing_votes.empty():
            submission = await self.submissions_needing_votes.get()
            submissions.append(submission)
        self.schema = self.voting_method.get_vote_schema(
            num_submissions=len(submissions)
        )
        return submissions

    def get_results(self) -> Dict[str, Any]:
        logging.info("Processing votes for topic %s.", self.topic.uuid)
        self.results.process_votes(self.voting_method, self.submission_ids)
        return self.results.to_json()


class VotingManagerFactory:
    """
    Factory class for creating VotingManager instances based on the provided voting method.
    """

    @staticmethod
    def create_voting_manager(
        voting_method: str, topic: "Topic", **kwargs
    ) -> VotingManager:
        """
        Create a VotingManager instance based on the provided voting method.

        Args:
            voting_method (str): The name of the voting method to use.
            topic (Topic): The topic associated with the voting manager.
            **kwargs: Additional keyword arguments.

        Returns:
            VotingManager: An instance of VotingManager configured with the specified voting method.

        Raises:
            ValueError: If an invalid voting method is provided.
        """
        voting_method_class = get_voting_method(voting_method)
        if voting_method_class.is_label():
            return LabelVotingManager(voting_method_class, topic, **kwargs)
        return CompareVotingManager(voting_method_class, topic, **kwargs)
