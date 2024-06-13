# models/session.py

import logging
from ciwa.config.logging_config import setup_logging
import asyncio
import json
from typing import List, Optional, Dict, Any
from ciwa.models.topic import Topic, TopicFactory
from ciwa.models.participants.participant import Participant
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.submission import Submission
from ciwa.models.identifiable import Identifiable
import time


class Session(Identifiable):
    """
    Represents a session within the CIwA system.
    """

    def __init__(
        self,
        process: Optional["Process"] = None,
        topics_config: List[Dict[str, Any]] = [],
        default_topic_settings: Dict[str, Any] = {},
        participants_config: List[Dict[str, Any]] = [],
        max_subs_per_topic: int = 1,
        max_concurrent: int = 50,
        save_results: bool = True,
        **kwargs,
    ) -> None:
        super().__init__()
        self.process: Optional["Process"] = process
        self.name: str = kwargs.get("name", "Session")
        self.description: str = kwargs.get("description", "A Session.")
        self.is_complete: bool = False
        self.topics: List[Topic] = self._init_topics(
            topics_config, default_topic_settings
        )
        self.participants: List[Participant] = self._init_participants(
            participants_config
        )
        self.max_concurrent: int = max_concurrent
        self.max_subs_per_topic: int = max_subs_per_topic
        self.results: Dict[str, Any] = {}
        self.save_results: bool = save_results
        logging.info(f"Session initialized with UUID: {self.uuid}")
        logging.info(f"Session topics: {[topic.title for topic in self.topics]}")

    def _init_topics(
        self,
        topics_config: List[Dict[str, Any]],
        default_topic_settings: Dict[str, Any],
    ) -> List[Topic]:
        topics = [
            TopicFactory.create_topic(
                session=self, **{**default_topic_settings, **topic_config}
            )
            for topic_config in topics_config
        ]
        return topics

    def _init_participants(
        self, participants_config: List[Dict[str, Any]]
    ) -> List[Participant]:
        participants = [
            ParticipantFactory.create_participant(**participant_config)
            for participant_config in participants_config
        ]
        return participants

    def add_participant(self, participant: Participant) -> None:
        """
        Add a participant to the session.
        """
        self.participants.append(participant)

    def add_participant(self, participant_config: Dict[str, Any]) -> None:
        """
        Add a participant from a config dict to the session.
        """

        new_participant = ParticipantFactory.create_participant(**participant_config)

        self.participants.append(new_participant)

        logging.info(f"Added new participant: {new_participant.uuid}")

    def add_participants(self, participants_config: List[Dict[str, Any]]) -> None:
        """
        Add multiple participants to the session.
        """
        for participant_config in participants_config:
            self.add_participant(participant_config)

    def add_topic(
        self, topic_config: Dict[str, Any], default_topic_settings: Dict[str, Any] = {}
    ) -> None:

        new_topic = TopicFactory.create_topic(
            session=self, **{**default_topic_settings, **topic_config}
        )

        self.topics.append(new_topic)

        logging.info(f"Added new topic: {new_topic.title}")

    async def gather_submissions(self) -> None:
        """
        Gathers submissions from participants for each topic by using an asynchronous generator,
        allowing each submission to be processed as soon as it is generated.
        """
        tasks = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        for topic in self.topics:
            for participant in self.participants:
                for _ in range(self.max_subs_per_topic):
                    async with semaphore:
                        task = asyncio.create_task(
                            self.create_submission_task(participant, topic)
                        )
                        tasks.append(task)
        await asyncio.gather(*tasks)
        logging.info("All submissions gathered.")

    async def create_submission_task(
        self, participant: Participant, topic: Topic
    ) -> None:
        """
        Creates a submission task for a given participant and topic.

        Args:
            participant (Participant): The participant generating the submission.
            topic (Topic): The topic for which the submission is created.
        """
        start_time = time.time()
        submission = await participant.create_submission(topic)
        if submission is not None:
            await topic.add_submission(submission)
            logging.info(
                f"TIMING: Submission {submission.uuid} generated by {participant.__class__.__name__} in {time.time() - start_time:.2f} seconds"
            )

    async def run(self) -> None:
        """
        Run the session by conducting activities asynchronously.
        """
        logging.info(f"Running session {self.uuid}.")
        start_time = time.time()
        await self.gather_submissions()
        await self.collect_all_votes()
        await self.gather_results()
        self.conclude()
        total_elapsed_time = time.time() - start_time
        logging.info(
            f"TIMING: Total elapsed time for session {self.uuid}: {total_elapsed_time:.2f} seconds"
        )

    def conclude(self) -> None:
        """
        Conclude the session.
        """
        self.is_complete = True
        logging.info(f"Session {self.uuid} completed.")
        if self.save_results:
            self.save_results()

    async def collect_all_votes(self) -> None:
        logging.info("Collecting votes on topics.")
        tasks = []
        for topic in self.topics:
            start_time = time.time()
            task = asyncio.create_task(
                self._collect_votes_with_logging(topic, start_time)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def _collect_votes_with_logging(
        self, topic: Topic, start_time: float
    ) -> None:
        await topic.voting_manager.collect_votes(self.participants)
        logging.info(
            f"TIMING: Votes collected for topic '{topic.title}' in {time.time() - start_time:.2f} seconds"
        )

    async def gather_results(self) -> None:
        logging.info("Gathering results from all topics.")
        self.results = {
            "session": {
                "uuid": self.uuid,
                "name": self.name,
                "description": self.description,
            },
            "topics": [],
            "participants": [
                participant.to_json() for participant in self.participants
            ],
        }
        for topic in self.topics:
            topic_data = topic.to_json()
            voting_results = topic.voting_manager.get_results()
            topic_data["voting_results"] = voting_results
            self.results["topics"].append(topic_data)

    def save_results(self) -> None:
        results_file = f"{self.get_id_str()}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=4)
        logging.info(f"Results saved to {results_file}")

    @staticmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent a Session object's properties.
        """
        return {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["uuid", "name", "description"],
        }

    def to_json(self) -> dict:
        """
        Returns the JSON representation of the Session object.
        """
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "topics": [topic.to_json() for topic in self.topics],
            "participants": [
                participant.to_json() for participant in self.participants
            ],
        }


class SessionFactory:
    @staticmethod
    def create_session(process: "Process" = None, **kwargs) -> Session:
        """
        Create a Session instance with flexible parameter input.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected keys:
                - process (Process): The process to which the session belongs.
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
        session_default_topic_settings = kwargs.pop("default_topic_settings", {})
        if process:
            process_default_topic_settings = process.default_session_settings.get(
                "default_topic_settings", {}
            )
            # Merge process default topic settings with session default topic settings
            default_topic_settings = {
                **process_default_topic_settings,
                **session_default_topic_settings,
            }
        else:
            default_topic_settings = session_default_topic_settings

        participant_configs = kwargs.pop("participants", [])

        session = Session(
            process=process,
            name=name,
            description=description,
            topics_config=topics_config,
            default_topic_settings=default_topic_settings,
            participants_config=participant_configs,
            **kwargs,
        )

        return session
