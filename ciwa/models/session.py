# filename: ciwa/models/session.py

import logging
import asyncio
from uuid import UUID, uuid4
from typing import List, Optional, Tuple
from ciwa.models.topic import Topic, TopicFactory
from ciwa.models.participants.participant import Participant
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.submission import Submission

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Session:
    """
    Represents a session within the CIwA system.
    """

    def __init__(
        self,
        topics: List[Topic] = [],
        max_subs_per_topic: int = 1,
        max_concurrent: int = 10,
        **kwargs,
    ) -> None:
        self.uuid: UUID = uuid4()
        self.name: str = kwargs.get("name", "Session")
        self.description: str = kwargs.get("description", "A Session.")
        self.is_complete: bool = False
        self.topics: List[Topic] = topics
        self.participants: List[Participant] = []
        self.max_concurrent: int = max_concurrent
        self.max_subs_per_topic: int = max_subs_per_topic
        logging.info(f"Session initialized with UUID: {self.uuid}")
        logging.info(f"Session topics: {[topic.title for topic in self.topics]}")

    def add_participant(self, participant: Participant) -> None:
        """
        Add a participant to the session.
        """
        self.participants.append(participant)

    async def gather_submissions(self) -> None:
        """
        Gathers submissions from participants for each topic by using an asynchronous generator,
        allowing each submission to be processed as soon as it is generated.
        """
        tasks = []
        for topic in self.topics:
            for participant in self.participants:
                task = asyncio.create_task(self.handle_submissions(topic, participant))
                tasks.append(task)
        await asyncio.gather(*tasks)
        logging.info("All submissions gathered.")

    async def run(self) -> None:
        """
        Run the session by conducting activities asynchronously.
        """
        logging.info(f"Running session {self.uuid}.")
        await self.gather_submissions()
        self.conclude()

    def conclude(self) -> None:
        """
        Conclude the session.
        """
        # Placeholder logic for session conclusion
        self.is_complete = True
        logging.info(f"Session {self.uuid} completed.")

    async def handle_submissions(self, topic: Topic, participant: Participant) -> None:
        """
        Handles the asynchronous generation of submissions for a given topic by a participant.

        This method manages the generation and addition of submissions using a semaphore
        to control concurrency.

        Args:
            topic (Topic): The topic for which submissions are being generated.
            participant (Participant): The participant generating submissions.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        async with semaphore:
            async for submission in participant.generate_submissions(
                topic, self.max_subs_per_topic
            ):
                await topic.add_submission(submission)


class SessionFactory:
    @staticmethod
    def create_session(**kwargs) -> Session:
        """
        Create a Session instance with flexible parameter input.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected keys:
                - name (str): Name of the session.
                - description (str): Detailed description of the session.
                - topics_config (list): List of configurations for topics within this session.
                - default_topic_settings (dict, optional): Default settings for topics in this session.
                - participants (list, optional): List of participant configurations.

        Returns:
            Session: An instance of Session configured as specified by the input parameters.
        """
        name = kwargs.pop("name", "Default Session Name")
        description = kwargs.pop("description", "No description provided.")
        topics_config = kwargs.pop("topics", [])
        default_topic_settings = kwargs.pop("default_topic_settings", {})
        participant_configs = kwargs.pop("participants", [])

        # Create topics using the TopicFactory, applying default settings
        topics = [
            TopicFactory.create_topic(**{**default_topic_settings, **topic_config})
            for topic_config in topics_config
        ]

        # Create participants
        participants = [
            ParticipantFactory.create_participant(**participant_config)
            for participant_config in participant_configs
        ]

        session = Session(name=name, description=description, topics=topics, **kwargs)

        for participant in participants:
            session.add_participant(participant)

        return session
