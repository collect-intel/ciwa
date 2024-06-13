import asyncio
import logging
from typing import List, Type, Dict, Any
import jsonschema
from ciwa.models.voting_methods.voting_method import VotingMethod
from ciwa.models.voting_methods.enum_label import EnumLabel
from ciwa.models.voting_methods.yes_no_label import YesNoLabel
from ciwa.models.voting_methods.ranking_compare import RankingCompare
from ciwa.models.voting_methods.score_label import ScoreLabel
from ciwa.models.voting_methods.score_compare import ScoreCompare
from ciwa.models.submission import Submission
from ciwa.models.voting_results import LabelVotingResults, CompareVotingResults
import time
from abc import ABC, abstractmethod


class VotingManager(ABC):
    """
    Abstract base class for managing the voting process for a given topic using a specified voting voting_method.

    Attributes:
        voting_method (VotingMethod): The voting voting_method to use for this topic.
        submissions_needing_votes (asyncio.Queue[Submission]): Queue of submissions needing votes.
        results (VotingResults): Instance to hold and manage voting results.
        schema (Dict[str, Any]): The JSON schema for the vote data.
        submission_ids (List[str]): List of submission.uuid's that were made available for voting.
    """

    def __init__(
        self,
        voting_method_class: Type[VotingMethod],
        topic: "Topic",
        **kwargs,
    ) -> None:
        self.topic = topic
        self.voting_method: VotingMethod = voting_method_class(**kwargs)
        self.submissions_needing_votes: asyncio.Queue[Submission] = asyncio.Queue()
        self.submission_ids: List[str] = []
        self.results: "VotingResults" = self.initialize_results()
        logging.info(
            f"VotingManager initialized with voting_method: {self.voting_method.__class__.__name__}"
        )

    @abstractmethod
    def initialize_results(self) -> "VotingResults":
        """
        Initialize the appropriate VotingResults instance.
        """
        pass

    def add_submission(self, submission: Submission) -> None:
        self.submissions_needing_votes.put_nowait(submission)
        self.submission_ids.append(submission.uuid)

    @abstractmethod
    async def collect_votes(self, participants: List["Participant"]) -> None:
        pass

    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        pass


class LabelVotingManager(VotingManager):

    def __init__(
        self,
        voting_method_class: Type[VotingMethod],
        topic: "Topic",
        **kwargs,
    ) -> None:
        super().__init__(voting_method_class, topic, **kwargs)
        self.schema = self.voting_method.get_vote_schema()
        self.is_label = True

    def initialize_results(self) -> "VotingResults":
        return LabelVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            f"Collecting label votes for submissions on topic {self.topic.uuid} from participants."
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
                f"TIMING: Label votes collected for submission {submission.uuid} in {time.time() - vote_start_time:.2f} seconds"
            )

    async def collect_label_vote(
        self, participant: "Participant", submission: Submission
    ) -> None:
        vote_json = await participant.get_label_vote_response(
            submission=submission,
            vote_schema=self.schema,
            vote_prompt=self.voting_method.get_vote_prompt(submission),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, {submission.uuid: vote_json})
        except jsonschema.ValidationError as e:
            logging.error(f"Invalid vote data: {e.message}")

    def get_results(self) -> Dict[str, Any]:
        logging.info(f"Processing votes for topic {self.topic.uuid}.")
        self.results.process_votes(self.voting_method, self.submission_ids)
        return self.results.to_json()


class CompareVotingManager(VotingManager):

    def __init__(
        self,
        voting_method_class: Type[VotingMethod],
        topic: "Topic",
        **kwargs,
    ) -> None:
        super().__init__(voting_method_class, topic, **kwargs)
        self.schema = None
        self.is_label = False

    def initialize_results(self) -> "VotingResults":
        return CompareVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            f"Collecting compare votes for submissions on topic {self.topic.uuid} from participants."
        )
        submissions = await self.get_all_submissions()
        tasks = [
            asyncio.create_task(self.collect_compare_vote(participant, submissions))
            for participant in participants
        ]
        await asyncio.gather(*tasks)

    async def collect_compare_vote(
        self, participant: "Participant", submissions: List[Submission]
    ) -> None:
        vote_json = await participant.get_compare_vote_response(
            submissions=submissions,
            vote_schema=self.schema,
            vote_prompt=self.voting_method.get_vote_prompt(submissions),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, vote_json)
            logging.info(
                f"Compare vote for topic {self.topic.uuid} from participant {participant.uuid} added to results."
            )
        except jsonschema.ValidationError as e:
            logging.error(f"Invalid vote data: {e.message}")

    async def get_all_submissions(self) -> List[Submission]:
        submissions = []
        while not self.submissions_needing_votes.empty():
            submission = await self.submissions_needing_votes.get()
            submissions.append(submission)
        self.schema = self.voting_method.get_vote_schema(
            num_submissions=len(submissions)
        )
        return submissions

    def get_results(self) -> Dict[str, Any]:
        logging.info(f"Processing votes for topic {self.topic.uuid}.")
        self.results.process_votes(self.voting_method, self.submission_ids)
        return self.results.to_json()


class VotingManagerFactory:
    @staticmethod
    def create_voting_manager(
        voting_method: str,
        topic: "Topic",
        **kwargs,
    ) -> VotingManager:
        """
        Create a VotingManager instance based on the provided voting_method.

        Args:
            voting_method (str): The name of the voting voting_method to use.
            topic (Topic): The topic associated with the voting manager.
            **kwargs: Additional keyword arguments.

        Returns:
            VotingManager: An instance of VotingManager configured with the specified voting_method.
        """
        voting_method_class = globals().get(voting_method)
        if voting_method_class and issubclass(voting_method_class, VotingMethod):
            if voting_method_class.is_label():
                return LabelVotingManager(voting_method_class, topic, **kwargs)
            else:
                return CompareVotingManager(voting_method_class, topic, **kwargs)
        else:
            raise ValueError(f"Invalid voting voting_method provided: {voting_method}")
