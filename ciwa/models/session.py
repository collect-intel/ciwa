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
        process: "Process",
        topics_config: List[Dict[str, Any]] = [],
        default_topic_settings: Dict[str, Any] = {},
        participants_config: List[Dict[str, Any]] = [],
        max_subs_per_topic: int = 1,
        max_concurrent: int = 20,
        **kwargs,
    ) -> None:
        super().__init__()
        self.process: "Process" = process
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
                if submission is not None:
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
        self.results = {
            "session": {
                "uuid": self.uuid,
                "name": self.name,
                "description": self.description,
            },
            "topics": [],
            "participants": [
                participant.get_object_json() for participant in self.participants
            ],
        }
        for topic in self.topics:
            topic_data = topic.get_object_json()
            topic_data["submissions"] = []
            processed_votes = topic.voting_manager.process_votes()
            while not topic.submissions.empty():
                submission = await topic.submissions.get()
                submission_data = submission.get_object_json()
                submission_data["votes"] = processed_votes.get(
                    submission.get_id_str(), {}
                )
                topic_data["submissions"].append(submission_data)
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

    def get_object_json(self) -> dict:
        """
        Returns the JSON representation of the Session object.
        """
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "topics": [topic.get_object_json() for topic in self.topics],
            "participants": [
                participant.get_object_json() for participant in self.participants
            ],
        }


class SessionFactory:
    @staticmethod
    def create_session(process: "Process", **kwargs) -> Session:
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
        default_topic_settings = kwargs.pop("default_topic_settings", {})
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
