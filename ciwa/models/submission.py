# filename: ciwa/models/submission.py
from typing import List, Optional
import datetime
from ciwa.models.identifiable import Identifiable


class Submission(Identifiable):
    """
    Represents a submission made by a participant on a particular topic.

    Attributes:
        topic (Topic): The topic to which this submission belongs.
        participant (Participant): The participant who made the submission.
        content (str): The actual content of the submission.
        created_at (datetime.datetime): The timestamp when the submission was created.
        votes (asyncio.Queue): A queue to handle votes asynchronously.
    """

    def __init__(self, topic: "Topic", participant: "Participant", content: str):
        super().__init__()
        self.topic = topic
        self.participant = participant
        self.content = content
        self.created_at = datetime.datetime.now()

    def __str__(self) -> str:
        return f"Submission {self.uuid} by {self.participant.identifier} on '{self.topic.title}' at {self.created_at}: {self.content[:50]}..."
