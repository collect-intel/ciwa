# models/session.py

"""
This module defines the Session class and its associated factory, which represent
a session within the CIwA system, managing topics and participants.
"""

import logging
import asyncio
import json
import time
from typing import List, Optional, Dict, Any
from ciwa.models.identifiable import Identifiable
from ciwa.models.participants.participant_factory import ParticipantFactory
from ciwa.models.topic import TopicFactory


class Session(Identifiable):
    """
    Represents a session within the CIwA system.

    Attributes:
        process (Optional[Process]): The process to which the session belongs.
        name (str): The name of the session.
        description (str): The description of the session.
        is_complete (bool): Indicates if the session is complete.
        topics (List[Topic]): The topics in the session.
        participants (List[Participant]): The participants in the session.
        max_concurrent (int): Maximum concurrent tasks.
        max_subs_per_topic (int): Maximum submissions per topic.
        results (Dict[str, Any]): The results of the session.
        do_save_results (bool): Indicates if results should be saved.
    """

    def __init__(
        self,
        process: Optional["Process"] = None,
        topics_config: Optional[List[Dict[str, Any]]] = None,
        default_topic_settings: Optional[Dict[str, Any]] = None,
        participants_config: Optional[List[Dict[str, Any]]] = None,
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
        self.topics: List["Topic"] = self._init_topics(
            topics_config or [], default_topic_settings or {}
        )
        self.participants: List["Participant"] = self._init_participants(
            participants_config or []
        )
        self.max_concurrent: int = max_concurrent
        self.max_subs_per_topic: int = max_subs_per_topic
        self.results: Dict[str, Any] = {}
        self.do_save_results: bool = save_results
        logging.info("Session initialized with UUID: %s", self.uuid)
        logging.info("Session topics: %s", [topic.title for topic in self.topics])

    def _init_topics(
        self,
        topics_config: List[Dict[str, Any]],
        default_topic_settings: Dict[str, Any],
    ) -> List["Topic"]:

        return [
            TopicFactory.create_topic(
                session=self, **{**default_topic_settings, **topic_config}
            )
            for topic_config in topics_config
        ]

    def _init_participants(
        self, participants_config: List[Dict[str, Any]]
    ) -> List["Participant"]:

        return [
            ParticipantFactory.create_participant(**participant_config)
            for participant_config in participants_config
        ]

    def add_participant(self, participant_config: Dict[str, Any]) -> None:
        """
        Add a participant from a config dict to the session.
        """
        new_participant = ParticipantFactory.create_participant(**participant_config)
        self.participants.append(new_participant)
        logging.info("Added new participant: %s", new_participant.uuid)

    def add_participants(self, participants_config: List[Dict[str, Any]]) -> None:
        """
        Add multiple participants to the session.
        """
        for participant_config in participants_config:
            self.add_participant(participant_config)

    def add_topic(
        self, topic_config: Dict[str, Any], default_topic_settings: Dict[str, Any] = {}
    ) -> None:
        """
        Add a new topic to the session.
        """
        new_topic = TopicFactory.create_topic(
            session=self, **{**default_topic_settings, **topic_config}
        )
        self.topics.append(new_topic)
        logging.info("Added new topic: %s", new_topic.title)

    async def gather_submissions(self) -> None:
        """
        Gathers submissions from participants for each topic asynchronously.
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
        self, participant: "Participant", topic: "Topic"
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
                "TIMING: Submission %s generated by %s in %.2f seconds",
                submission.uuid,
                participant.__class__.__name__,
                time.time() - start_time,
            )

    async def run(self) -> None:
        """
        Run the session by conducting activities asynchronously.
        """
        logging.info("Running session %s.", self.uuid)
        start_time = time.time()
        await self.gather_submissions()
        await self.collect_all_votes()
        await self.gather_results()
        self.conclude()
        total_elapsed_time = time.time() - start_time
        logging.info(
            "TIMING: Total elapsed time for session %s: %.2f seconds",
            self.uuid,
            total_elapsed_time,
        )

    def conclude(self) -> None:
        """
        Conclude the session.
        """
        self.is_complete = True
        logging.info("Session %s completed.", self.uuid)
        if self.do_save_results:
            self.save_results()

    async def collect_all_votes(self) -> None:
        """
        Collect votes from all participants for each topic.
        """
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
        self, topic: "Topic", start_time: float
    ) -> None:
        """
        Collect votes for a topic and log the time taken.

        Args:
            topic (Topic): The topic for which votes are being collected.
            start_time (float): The start time of the vote collection.
        """
        await topic.voting_manager.collect_votes(self.participants)
        logging.info(
            "TIMING: Votes collected for topic '%s' in %.2f seconds",
            topic.title,
            time.time() - start_time,
        )

    async def gather_results(self) -> None:
        """
        Gather results from all topics.
        """
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
        """
        Save the session results to a JSON file.
        """
        results_file = f"{self.get_id_str()}_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4)
        logging.info("Results saved to %s", results_file)

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
    """
    Factory class for creating Session instances.
    """

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
                - default_topic_settings (dict, optional): Default settings for topics in this
                session.
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

        return Session(
            process=process,
            name=name,
            description=description,
            topics_config=topics_config,
            default_topic_settings=default_topic_settings,
            participants_config=participant_configs,
            **kwargs,
        )
