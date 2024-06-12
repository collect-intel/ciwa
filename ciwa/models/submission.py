# models/submission.py

from typing import TYPE_CHECKING
import datetime
from ciwa.models.identifiable import Identifiable

if TYPE_CHECKING:
    from ciwa.models.topic import Topic
    from ciwa.models.participants.participant import Participant


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
        self.topic = topic
        self.participant = participant
        self.content = content
        self.created_at = datetime.datetime.now()

    def __str__(self) -> str:
        return f"Submission {self.uuid} by {self.participant.identifier} on '{self.topic.title}' at {self.created_at}: {self.content[:50]}..."

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

    def to_json(self) -> dict:
        """
        Returns a JSON representation of the Submission object.
        """
        return {
            "uuid": self.uuid,
            "participant_uuid": self.participant.uuid,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def get_response_schema() -> dict:
        """
        Returns the JSON schema to represent the properties a Participant is expected to respond with to create a Submission.
        """
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
            },
            "required": ["content"],
        }
