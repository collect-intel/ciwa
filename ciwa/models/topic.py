# models/topic.py

"""
This module defines the Topic and TopicFactory classes, which are responsible for managing topics
in a discussion or debate platform. Topics can handle submissions and apply a voting method.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Dict, Any, List
from ciwa.models.voting_manager import VotingManagerFactory
from ciwa.models.identifiable import Identifiable

if TYPE_CHECKING:
    from ciwa.models.session import Session


class Topic(Identifiable):
    """
    Represents a topic in a discussion or debate platform, capable of handling submissions
    and applying a voting method.

    Attributes:
        session (Session): The session to which this topic belongs.
        title (str): The title of the topic.
        description (str): A detailed description of what the topic is about.
        voting_manager (VotingManager): The voting manager that handles vote processing for
                                        this topic.
        submissions (asyncio.Queue): A queue to store submissions made to this topic.
    """

    def __init__(
        self,
        session: "Session",
        title: str,
        description: str,
        voting_method: str,
        voting_method_config: Dict[str, Any] = None,
        **kwargs,
    ) -> None:
        super().__init__()
        self.session: "Session" = session
        self.title: str = title
        self.description: str = description
        self.submissions: List["Submission"] = []
        self.submissions_queue: asyncio.Queue = asyncio.Queue()
        self.voting_manager = VotingManagerFactory.create_voting_manager(
            voting_method=voting_method,
            topic=self,
            **(voting_method_config or {}),
        )
        logging.info("Topic initialized with UUID: %s", self.uuid)

    async def add_submission(self, submission: "Submission") -> None:
        """
        Asynchronously adds a submission to the topic's queue of submissions.

        Args:
            submission (Submission): The submission to add to the topic.
        """
        await self.submissions_queue.put(submission)
        self.submissions.append(submission)
        self.voting_manager.add_submission(submission)
        logging.info(
            "Submission %s added to Topic %s with UUID: %s",
            submission.uuid,
            self.title,
            self.uuid,
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
                "voting_method": {"type": "string"},
            },
            "required": ["uuid", "title", "description", "voting_method"],
        }

    def to_json(self) -> dict:
        """
        Returns the JSON representation of the Topic object.
        """
        return {
            "uuid": str(self.uuid),
            "title": self.title,
            "description": self.description,
            "voting_method": self.voting_manager.voting_method.__class__.__name__,
            "submissions": [submission.to_json() for submission in self.submissions],
        }


class TopicFactory:
    """
    Factory class for creating Topic instances with flexible parameter input.

    Methods:
        create_topic: Creates a Topic instance.
    """

    @staticmethod
    def create_topic(session: "Session", **kwargs) -> Topic:
        """
        Create a Topic instance with flexible parameter input.

        Args:
            session (Session): The session to which this topic belongs.
            **kwargs: Arbitrary keyword arguments. Expected keys:
                - title (str): Title of the topic.
                - description (str): Detailed description of the topic.
                - voting_method (str, optional): Method for voting, defaults to 'YesNoLabel'.
                - voting_method_config (dict, optional): Configuration for the voting method.

        Returns:
            Topic: An instance of Topic configured as specified by the input parameters.
        """
        title = kwargs.get("title", "Default Topic Title")
        description = kwargs.get("description", "No description provided.")
        voting_method_config = kwargs.pop("voting_method", {})
        voting_method = voting_method_config.pop("type", "YesNoLabel")

        return Topic(
            session=session,
            title=title,
            description=description,
            voting_method=voting_method,
            voting_method_config=voting_method_config,
        )
