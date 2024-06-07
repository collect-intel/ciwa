# filename: ciwa/models/topic.py

from ciwa.models.voting_manager import VotingManagerFactory
import logging
import asyncio
from ciwa.models.identifiable import Identifiable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Topic(Identifiable):
    """
    Represents a topic in a discussion or debate platform, capable of handling submissions and applying a voting strategy.

    Attributes:
        title (str): The title of the topic.
        description (str): A detailed description of what the topic is about.
        voting_manager (VotingManager): The voting manager that handles vote processing for this topic.
        submissions (asyncio.Queue): A queue to store submissions made to this topic.
    """

    def __init__(
        self,
        title: str,
        description: str,
        voting_strategy: str,
        voting_strategy_config: dict = {},
        **kwargs,
    ) -> None:
        """
        Initializes a new Topic with a title, description, and a specified voting strategy.

        Args:
            title (str): The title of the topic.
            description (str): The description of the topic.
            voting_strategy (str): The name of the voting strategy to be used with this topic.
            **kwargs: Additional keyword arguments that might be used for future extensions.
        """
        super().__init__()
        self.title: str = title
        self.description: str = description
        self.submissions = asyncio.Queue()
        self.voting_manager = VotingManagerFactory.create_voting_manager(
            strategy=voting_strategy,
            submissions=self.submissions,
            topic=self,
            **voting_strategy_config,
        )
        logging.info(f"Topic initialized with UUID: {self.uuid}")

    async def add_submission(self, submission: "Submission") -> None:
        """
        Asynchronously adds a submission to the topic's queue of submissions.

        Args:
            submission (Submission): The submission to add to the topic.
        """
        await self.submissions.put(submission)
        logging.info(
            f"Submission {submission.uuid} added to Topic {self.title} with UUID: {self.uuid}"
        )


class TopicFactory:
    @staticmethod
    def create_topic(**kwargs) -> Topic:
        """
        Create a Topic instance with flexible parameter input.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected keys:
                - title (str): Title of the topic.
                - description (str): Detailed description of the topic.
                - voting_strategy (str, optional): Strategy for voting, defaults to 'YesNoLabeling'.
                - max_submissions (int, optional): Maximum submissions allowed, defaults to 10.

        Returns:
            Topic: An instance of Topic configured as specified by the input parameters.
        """
        # Extract values from kwargs or use defaults
        title = kwargs.get("title", "Default Topic Title")
        description = kwargs.get("description", "No description provided.")
        voting_strategy_config = kwargs.pop("voting_strategy", {})
        voting_strategy = voting_strategy_config.pop("type", "YesNoLabeling")
        max_submissions = kwargs.get("max_submissions", 10)

        # Return a new Topic instance
        return Topic(
            title=title,
            description=description,
            voting_strategy=voting_strategy,
            max_submissions=max_submissions,
            voting_strategy_config=voting_strategy_config,
        )
