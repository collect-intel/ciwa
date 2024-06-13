import asyncio
import logging
from typing import List, Type, Dict, Any
import jsonschema
from ciwa.models.voting_strategies.voting_strategy import VotingStrategy
from ciwa.models.voting_strategies.enum_labeling import EnumLabeling
from ciwa.models.voting_strategies.yes_no_labeling import YesNoLabeling
from ciwa.models.voting_strategies.ranking_comparison import RankingComparison
from ciwa.models.voting_strategies.score_labeling import ScoreLabeling
from ciwa.models.voting_strategies.score_comparison import ScoreComparison
from ciwa.models.submission import Submission
from ciwa.models.voting_results import LabelVotingResults, ComparativeVotingResults
import time
from abc import ABC, abstractmethod


class VotingManager(ABC):
    """
    Abstract base class for managing the voting process for a given topic using a specified voting strategy.

    Attributes:
        strategy (VotingStrategy): The voting strategy to use for this topic.
        submissions_needing_votes (asyncio.Queue[Submission]): Queue of submissions needing votes.
        results (VotingResults): Instance to hold and manage voting results.
        schema (Dict[str, Any]): The JSON schema for the vote data.
        submission_ids (List[str]): List of submission.uuid's that were made available for voting.
    """

    def __init__(
        self,
        strategy_class: Type[VotingStrategy],
        topic: "Topic",
        **kwargs,
    ) -> None:
        self.topic = topic
        self.strategy: VotingStrategy = strategy_class(**kwargs)
        self.submissions_needing_votes: asyncio.Queue[Submission] = asyncio.Queue()
        self.submission_ids: List[str] = []
        self.results: "VotingResults" = self.initialize_results()
        logging.info(
            f"VotingManager initialized with strategy: {self.strategy.__class__.__name__}"
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


class LabelingVotingManager(VotingManager):

    def __init__(
        self,
        strategy_class: Type[VotingStrategy],
        topic: "Topic",
        **kwargs,
    ) -> None:
        super().__init__(strategy_class, topic, **kwargs)
        self.schema = self.strategy.get_vote_schema()
        self.is_labeling = True

    def initialize_results(self) -> "VotingResults":
        return LabelVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            f"Collecting labeling votes for submissions on topic {self.topic.uuid} from participants."
        )
        while not self.submissions_needing_votes.empty():
            submission = await self.submissions_needing_votes.get()
            vote_start_time = time.time()
            tasks = [
                asyncio.create_task(self.collect_labeling_vote(participant, submission))
                for participant in participants
            ]
            await asyncio.gather(*tasks)
            logging.info(
                f"TIMING: Labeling votes collected for submission {submission.uuid} in {time.time() - vote_start_time:.2f} seconds"
            )

    async def collect_labeling_vote(
        self, participant: "Participant", submission: Submission
    ) -> None:
        vote_json = await participant.get_labeling_vote_response(
            submission=submission,
            vote_schema=self.schema,
            vote_prompt=self.strategy.get_vote_prompt(submission),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, {submission.uuid: vote_json})
        except jsonschema.ValidationError as e:
            logging.error(f"Invalid vote data: {e.message}")

    def get_results(self) -> Dict[str, Any]:
        logging.info(f"Processing votes for topic {self.topic.uuid}.")
        self.results.process_votes(self.strategy, self.submission_ids)
        return self.results.to_json()


class ComparativeVotingManager(VotingManager):

    def __init__(
        self,
        strategy_class: Type[VotingStrategy],
        topic: "Topic",
        **kwargs,
    ) -> None:
        super().__init__(strategy_class, topic, **kwargs)
        self.schema = None
        self.is_labeling = False

    def initialize_results(self) -> "VotingResults":
        return ComparativeVotingResults()

    async def collect_votes(self, participants: List["Participant"]) -> None:
        logging.info(
            f"Collecting comparative votes for submissions on topic {self.topic.uuid} from participants."
        )
        submissions = await self.get_all_submissions()
        tasks = [
            asyncio.create_task(self.collect_comparative_vote(participant, submissions))
            for participant in participants
        ]
        await asyncio.gather(*tasks)

    async def collect_comparative_vote(
        self, participant: "Participant", submissions: List[Submission]
    ) -> None:
        vote_json = await participant.get_comparative_vote_response(
            submissions=submissions,
            vote_schema=self.schema,
            vote_prompt=self.strategy.get_vote_prompt(submissions),
        )
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            self.results.add_vote(participant.uuid, vote_json)
            logging.info(
                f"Comparative vote for topic {self.topic.uuid} from participant {participant.uuid} added to results."
            )
        except jsonschema.ValidationError as e:
            logging.error(f"Invalid vote data: {e.message}")

    async def get_all_submissions(self) -> List[Submission]:
        submissions = []
        while not self.submissions_needing_votes.empty():
            submission = await self.submissions_needing_votes.get()
            submissions.append(submission)
        self.schema = self.strategy.get_vote_schema(num_submissions=len(submissions))
        return submissions

    def get_results(self) -> Dict[str, Any]:
        logging.info(f"Processing votes for topic {self.topic.uuid}.")
        self.results.process_votes(self.strategy, self.submission_ids)
        return self.results.to_json()


class VotingManagerFactory:
    @staticmethod
    def create_voting_manager(
        strategy: str,
        topic: "Topic",
        **kwargs,
    ) -> VotingManager:
        """
        Create a VotingManager instance based on the provided strategy.

        Args:
            strategy (str): The name of the voting strategy to use.
            topic (Topic): The topic associated with the voting manager.
            **kwargs: Additional keyword arguments.

        Returns:
            VotingManager: An instance of VotingManager configured with the specified strategy.
        """
        strategy_class = globals().get(strategy)
        if strategy_class and issubclass(strategy_class, VotingStrategy):
            if strategy_class.is_labeling():
                return LabelingVotingManager(strategy_class, topic, **kwargs)
            else:
                return ComparativeVotingManager(strategy_class, topic, **kwargs)
        else:
            raise ValueError(f"Invalid voting strategy provided: {strategy}")
