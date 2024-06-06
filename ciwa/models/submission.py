# filename: ciwa/models/submission.py
from typing import List, Optional
import datetime
import asyncio
from uuid import UUID, uuid4


class Submission:
    """
    Represents a submission made by a participant on a particular topic.

    Attributes:
        topic (Topic): The topic to which this submission is related.
        participant (Participant): The participant who made the submission.
        content (str): The actual content of the submission.
        created_at (datetime.datetime): The timestamp when the submission was created.
        votes (asyncio.Queue): A queue to handle votes asynchronously.
    """

    def __init__(self, topic: "Topic", participant: "Participant", content: str):
        self.topic = topic
        self.uuid: UUID = uuid4()
        self.participant = participant
        self.content = content
        self.created_at = datetime.datetime.now()
        self.votes = asyncio.Queue()

    def add_vote(self, vote: "Vote") -> None:
        """
        Adds a vote to the submission.

        Args:
            vote (Vote): The vote to be added to the submission.
        """
        self.votes.put(vote)

    def __str__(self) -> str:
        return f"Submission {self.uuid} by {self.participant.identifier} on '{self.topic.title}' at {self.created_at}: {self.content[:50]}..."
