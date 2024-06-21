# models/topic.py

"""
This module defines the Topic and TopicFactory classes, which are responsible for managing topics
in a discussion or debate platform. Topics can handle submissions and apply a voting method.
"""

import asyncio
import logging
from typing import Dict, Any, List, Callable
from ciwa.models.identifiable import Identifiable
from ciwa.models.voting_manager import VotingManagerFactory
from ciwa.models.schema_factory import SchemaFactory


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
        self.set_submission_validator(
            submission_validator=kwargs.get("submission_validator", None),
            submission_invalid_message=kwargs.get("submission_invalid_message", None),
        )
        self.set_submission_content_schema(
            schema=kwargs.get("submission_content_schema", {"type": "string"})
        )

        logging.info("Topic initialized with UUID: %s", self.uuid)

    async def add_submission(self, submission: "Submission") -> None:
        """
        Asynchronously adds a submission to the topic's queue of submissions if
        it passes the validation.

        Args:
            submission (Submission): The submission to add to the topic.
        """
        if self.submission_validator(submission):
            await self.submissions_queue.put(submission)
            self.submissions.append(submission)
            self.voting_manager.add_submission(submission)
            logging.info("Submission %s added to Topic %s", submission.uuid, self.title)
        else:
            logging.warning(
                "Submission %s is invalid for Topic %s: %s",
                submission.uuid,
                self.title,
                self.submission_invalid_message,
            )

    def set_submission_validator(
        self,
        submission_validator: Callable[[Any], bool] = None,
        submission_invalid_message: str = None,
    ) -> None:
        """
        Sets the submission validation function for this topic.

        Args:
            submission_validator (Callable[[Any], bool]): The function to validate submissions.
            submission_invalid_message (str): The message to return to a Participant when
            a submission is invalid.
        """
        self.submission_validator: Callable[[Any], bool] = submission_validator or (
            lambda x: True
        )
        self.submission_invalid_message: str = (
            submission_invalid_message or "Submission is invalid."
        )

    def set_submission_content_schema(self, schema: Dict[str, Any]) -> None:
        """
        Sets the schema for the content of a submission. Raises exception if schema is invalid.

        Args:
            schema (Dict[str, Any]): The schema for the content of a submission.
        """

        content_schema = SchemaFactory.create_object_schema("content", schema)
        SchemaFactory.validate_schema(content_schema)
        self.submission_content_schema: Dict[str, Any] = schema

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
        title = kwargs.pop("title", "")
        description = kwargs.pop("description", "")
        voting_method_config = kwargs.pop("voting_method", {})
        voting_method = voting_method_config.pop("type")

        return Topic(
            session=session,
            title=title,
            description=description,
            voting_method=voting_method,
            voting_method_config=voting_method_config,
            **kwargs,
        )
