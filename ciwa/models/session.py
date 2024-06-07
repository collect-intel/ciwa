# filename: ciwa/models/session.py

import logging
import asyncio
import json
from typing import List, Optional, Dict, Any
from ciwa.models.topic import Topic, TopicFactory
from ciwa.models.participants.participant import Participant
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.submission import Submission
from ciwa.models.identifiable import Identifiable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Session(Identifiable):
    """
    Represents a session within the CIwA system.
    """

    def __init__(
        self,
        topics: List[Topic] = [],
        max_subs_per_topic: int = 1,
        max_concurrent: int = 20,
        **kwargs,
    ) -> None:
        super().__init__()
        self.name: str = kwargs.get("name", "Session")
        self.description: str = kwargs.get("description", "A Session.")
        self.is_complete: bool = False
        self.topics: List[Topic] = topics
        self.participants: List[Participant] = []
        self.max_concurrent: int = max_concurrent
        self.max_subs_per_topic: int = max_subs_per_topic
        self.results: Dict[str, Dict[str, Any]] = {}
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
        await self.collect_all_votes()
        await self.gather_results()
        self.conclude()

    def conclude(self) -> None:
        """
        Conclude the session.
        """
        self.is_complete = True
        logging.info(f"Session {self.uuid} completed.")
        self.save_results()

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
                if topic.voting_manager.is_labeling:
                    await topic.voting_manager.collect_labeling_votes(
                        submission, self.participants
                    )

    async def collect_all_votes(self) -> None:
        logging.info("Collecting any comparative votes on topics.")
        tasks = []
        for topic in self.topics:
            if not topic.voting_manager.is_labeling:
                task = asyncio.create_task(
                    topic.voting_manager.collect_comparative_votes(self.participants)
                )
                tasks.append(task)
        await asyncio.gather(*tasks)

    async def gather_results(self) -> None:
        logging.info("Gathering results from all topics.")
        for topic in self.topics:
            self.results[topic.get_id_str()] = topic.voting_manager.process_votes()

    def save_results(self) -> None:
        results_file = f"{self.get_id_str()}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=4)
        logging.info(f"Results saved to {results_file}")


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
