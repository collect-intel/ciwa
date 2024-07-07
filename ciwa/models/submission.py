# models/submission.py

"""
This module provides the Submission class, representing a submission made by a participant
on a particular topic.
"""

import datetime
from typing import Any
from ciwa.models.identifiable import Identifiable


class Submission(Identifiable):
    """
    Represents a submission made by a participant on a particular topic.

    Attributes:
        topic (Topic): The topic to which this submission belongs.
        participant (Participant): The participant who made the submission.
        content (str): The actual content of the submission.
        created_at (datetime.datetime): The timestamp when the submission was created.
    """

    def __init__(
        self, topic: "Topic", participant: "Participant", content: str
    ) -> None:
        super().__init__()
        self.topic: "Topic" = topic
        self.participant: "Participant" = participant
        self.content: Any = content
        self.created_at = datetime.datetime.now()

    def __str__(self) -> str:
        return (
            f"Submission {self.uuid} by {self.participant.uuid} on "
            f"'{self.topic.title}' at {self.created_at}: {self.content[:50] if self.content else ""}..."
        )

    @staticmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent a Submission object's properties.
        """
        return {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "participant_uuid": {"type": "string"},
                "content": {"type": "string"},
                "created_at": {"type": "string"},
            },
            "required": ["uuid", "participant_uuid", "content", "created_at"],
        }

    @staticmethod
    def get_batch_submissions_schema(
        num_submissions: int, content_schema: dict
    ) -> dict:
        """
        Returns the JSON array schema to represent a batch of submissions.
        """
        return {
            "type": "array",
            "items": Submission.get_response_schema(content_schema),
            "minItems": num_submissions,
            "maxItems": num_submissions,
        }

    def to_json(self) -> dict:
        """
        Returns a JSON representation of the Submission object.
        """
        return {
            "uuid": self.uuid,
            "participant_uuid": self.participant.uuid,
            # TODO: modify content to_json to be adaptive to whether content is a str or more nested json
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def get_response_schema(content_schema: dict) -> dict:
        """
        Returns the JSON schema to represent the properties a Participant is expected to
        respond with to create a Submission.
        """
        return {
            "type": "object",
            "properties": {"content": content_schema},
            "required": ["content"],
        }
