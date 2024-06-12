# models/topic.py

import asyncio
import logging
from typing import TYPE_CHECKING, Dict, Any
from ciwa.models.voting_manager import VotingManagerFactory
from ciwa.models.identifiable import Identifiable

if TYPE_CHECKING:
    from ciwa.models.session import Session


class Topic(Identifiable):
    """
    Represents a topic in a discussion or debate platform, capable of handling submissions and applying a voting strategy.

    Attributes:
        session (Session): The session to which this topic belongs.
        title (str): The title of the topic.
        description (str): A detailed description of what the topic is about.
        voting_manager (VotingManager): The voting manager that handles vote processing for this topic.
        submissions (asyncio.Queue): A queue to store submissions made to this topic.
    """

    def __init__(
        self,
        session: "Session",
        title: str,
        description: str,
        voting_strategy: str,
        voting_strategy_config: Dict[str, Any] = {},
        **kwargs,
    ) -> None:
        super().__init__()
        self.session: "Session" = session
        self.title: str = title
        self.description: str = description
        self.submissions: "Queue" = asyncio.Queue()
        self.voting_manager = VotingManagerFactory.create_voting_manager(
            strategy=voting_strategy,
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
        self.voting_manager.add_submission(submission)
        logging.info(
            f"Submission {submission.uuid} added to Topic {self.title} with UUID: {self.uuid}"
        )

    @staticmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent a Topic object's properties.
        """
        return {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "voting_strategy": {"type": "string"},
            },
            "required": ["uuid", "title", "description", "voting_strategy"],
        }

    def to_json(self) -> dict:
        """
        Returns the JSON representation of the Topic object.
        """
        return {
            "uuid": str(self.uuid),
            "title": self.title,
            "description": self.description,
            "voting_strategy": self.voting_manager.strategy.__class__.__name__,
        }


class TopicFactory:
    @staticmethod
    def create_topic(session: "Session", **kwargs) -> Topic:
        """
        Create a Topic instance with flexible parameter input.

        Args:
            session (Session): The session to which this topic belongs.
            **kwargs: Arbitrary keyword arguments. Expected keys:
                - title (str): Title of the topic.
                - description (str): Detailed description of the topic.
                - voting_strategy (str, optional): Strategy for voting, defaults to 'YesNoLabeling'.
                - voting_strategy_config (dict, optional): Configuration for the voting strategy.

        Returns:
            Topic: An instance of Topic configured as specified by the input parameters.
        """
        title = kwargs.get("title", "Default Topic Title")
        description = kwargs.get("description", "No description provided.")
        voting_strategy_config = kwargs.pop("voting_strategy", {})
        voting_strategy = voting_strategy_config.pop("type", "YesNoLabeling")

        return Topic(
            session=session,
            title=title,
            description=description,
            voting_strategy=voting_strategy,
            voting_strategy_config=voting_strategy_config,
        )
