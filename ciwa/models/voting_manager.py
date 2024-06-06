# filename: ciwa/models/voting_manager.py
from typing import List, Type
from asyncio import Queue
from ciwa.models.voting_strategies.voting_strategy import VotingStrategy
from ciwa.models.voting_strategies.simple_majority import SimpleMajority
from ciwa.models.votes.vote_factory import VoteFactory
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VotingManager:
    """
    Manages the voting process for a given topic, using a specified voting strategy.

    Attributes:
        strategy (VotingStrategy): The voting strategy to use for this topic.
        submissions (Queue[Submission]): An asyncio.Queue() of Submissions to be voted on.
        vote_type (str): The type of vote used by the strategy.
        is_independent (bool): Whether the strategy is independent of other submissions.
    """

    def __init__(
        self, strategy_class: Type[VotingStrategy], submissions: Queue["Submission"]
    ) -> None:
        self.strategy: VotingStrategy = strategy_class()
        self.submissions: Queue["Submission"] = submissions
        self.vote_type: str = strategy_class.get_vote_type()
        self.is_independent: bool = self.strategy.is_independent()
        logging.info(
            f"VotingManager initialized with strategy: {self.strategy.__class__.__name__}"
        )

    # TODO: Possibly refactor or delete this method
    async def collect_votes(
        self, participant: "Participant", submissions: List["Submission"]
    ) -> None:
        if self.is_independent:
            for submission in submissions:
                vote = await participant.generate_independent_vote(
                    submission=submission
                )
                submission.add_vote(vote)
        else:
            vote = await participant.generate_comparative_vote(submissions=submissions)
            for submission in submissions:
                submission.add_vote(vote)

    # TODO: Possibly refactor or delete this method
    def create_vote(self, participant: "Participant", **kwargs) -> "Vote":
        """
        Creates a vote of the correct type for this voting strategy.

        Args:
            participant: The participant casting the vote.
            kwargs: Additional keyword arguments for vote creation.

        Returns:
            An instance of Vote.
        """
        return VoteFactory.create_vote(self.vote_type, participant, **kwargs)


class VotingManagerFactory:
    @staticmethod
    def create_voting_manager(
        strategy: str, submissions: Queue["Submission"]
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
            return VotingManager(strategy_class, submissions)
        else:
            raise ValueError("Invalid voting strategy provided.")
