# filename: ciwa/models/voting_manager.py
from typing import List, Type, Dict, Any
import asyncio
import jsonschema
from ciwa.models.voting_strategies.voting_strategy import VotingStrategy
from ciwa.models.voting_strategies.enum_labeling import EnumLabeling
from ciwa.models.voting_strategies.yes_no_labeling import YesNoLabeling
import logging
import pdb

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VotingManager:
    """
    Manages the voting process for a given topic, using a specified voting strategy.

    Attributes:
        strategy (VotingStrategy): The voting strategy to use for this topic.
        submissions (asyncio.Queue[Submission]): An asyncio.Queue() of Submissions to be voted on.
        vote_type (str): The type of vote used by the strategy.
        is_labeling (bool): Whether the strategy is labeling submissions independently of other submissions.
        participant_votes_data (Dict[str, Dict]): A dictionary of participant vote data.
        schema (Dict[str, Any]): The JSON schema for the vote data.
    """

    def __init__(
        self,
        strategy_class: Type[VotingStrategy],
        submissions: asyncio.Queue["Submission"],
        topic: "Topic",
        **kwargs,
    ) -> None:
        self.topic: "Topic" = topic
        self.strategy: VotingStrategy = strategy_class(**kwargs)
        self.submissions: asyncio.Queue["Submission"] = submissions
        self.vote_type: str = strategy_class.get_vote_type()
        self.is_labeling: bool = self.strategy.is_labeling()
        self.participant_votes_data: Dict[str, Dict] = {}
        self.schema: Dict[str, Any] = self.strategy.get_vote_schema()
        logging.info(
            f"VotingManager initialized with strategy: {self.strategy.__class__.__name__}"
        )

    async def collect_labeling_votes(
        self, submission: "Submission", participants: List["Participant"]
    ) -> None:
        logging.info(
            f"Collecting labeling votes for submission {submission.uuid} from participants."
        )
        tasks = []
        for participant in participants:
            task = asyncio.create_task(
                self.collect_labeling_vote(participant, submission)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def collect_labeling_vote(
        self, participant: "Participant", submission: "Submission"
    ) -> None:
        vote_json = await participant.get_labeling_vote_response(
            submission=submission, vote_schema=self.schema
        )
        # Validate vote data against schema
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            # Add vote data to participant_votes_data
            if participant.get_id_str() not in self.participant_votes_data:
                self.participant_votes_data[participant.get_id_str()] = {
                    "submissions": {}
                }
            self.participant_votes_data[participant.get_id_str()]["submissions"][
                submission.get_id_str()
            ] = vote_json
        except jsonschema.ValidationError as e:
            pdb.set_trace()
            logging.error(f"Invalid vote data: {e.message}")

    async def collect_comparative_votes(
        self, participants: List["Participant"]
    ) -> None:
        logging.info(
            f"Collecting comparative votes for submissions on topic {self.topic.uuid} from participants."
        )
        submissions = await self.get_all_submissions()
        tasks = []
        for participant in participants:
            task = asyncio.create_task(
                self.collect_comparative_vote(participant, submissions)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def collect_comparative_vote(
        self, participant: "Participant", submissions: List["Submission"]
    ) -> None:
        vote_json = await participant.get_comparative_vote_response(
            submissions=submissions, vote_schema=self.schema
        )
        # Validate vote data against schema
        try:
            jsonschema.validate(instance=vote_json, schema=self.schema)
            # Add vote data to participant_votes_data
            self.participant_votes_data[participant.get_id_str()] = vote_json
        except jsonschema.ValidationError as e:
            logging.error(f"Invalid vote data: {e.message}")

    async def get_all_submissions(self) -> List["Submission"]:
        submissions = []
        while not self.submissions.empty():
            submission = await self.submissions.get()
            submissions.append(submission)
        return submissions

    def process_votes(self) -> Dict[str, Any]:
        logging.info(f"Processing votes for topic {self.topic.uuid}.")
        results = self.strategy.process_votes(self.participant_votes_data)
        return results


class VotingManagerFactory:
    @staticmethod
    def create_voting_manager(
        strategy: str,
        submissions: asyncio.Queue["Submission"],
        topic: "Topic",
        **kwargs,
    ) -> VotingManager:
        """
        Create a VotingManager instance based on the provided strategy.

        Args:
            strategy (str): The name of the voting strategy to use.

        Returns:
            VotingManager: An instance of VotingManager configured with the specified strategy.
        """
        # Import the strategy class dynamically
        strategy_class = globals().get(strategy, None)
        if strategy_class and issubclass(strategy_class, VotingStrategy):
            return VotingManager(strategy_class, submissions, topic, **kwargs)
        else:
            raise ValueError(f"Invalid voting strategy provided: {strategy}")
