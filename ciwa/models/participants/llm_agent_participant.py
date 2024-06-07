# filename: ciwa/models/participants/llm_agent_participant.py

from ciwa.models.participants.participant import Participant
from ciwa.models.topic import Topic
from ciwa.models.submission import Submission
from typing import List, Dict, Any, AsyncGenerator
import asyncio
import logging
from ciwa.tests.utils import json_utils

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# for testing only:
SLEEP_DELAY = 0


class LLMAgentParticipant(Participant):
    """
    Represents an LLM (Large Language Model) Agent participant in the system.
    This class is responsible for generating submissions automatically based on a given topic.
    """

    def __init__(self, model: str, prompt_template: str):
        """
        Initializes a new instance of LLMAgentParticipant with a unique id.

        """
        super().__init__()
        self.model = model
        self.prompt_template = prompt_template
        logging.info(
            f"LLMAgentParticipant initialized with model: {self.model} and prompt_template: {self.prompt_template}"
        )

    async def generate_submissions(
        self, topic: Topic, num_submissions: int
    ) -> AsyncGenerator[Submission, None]:
        """
        Asynchronously generates submissions for a given topic, yielding each submission as it's created.

        Args:
            topic (Topic): The topic for which submissions are to be generated.
            num_submissions (int): The number of submissions to generate.

        Yields:
            Submission: A submission created for the specified topic.
        """
        logging.info(
            f"Generating {num_submissions} submissions for topic '{topic.title}' by LLMAgentParticipant {self.uuid}"
        )
        for _ in range(num_submissions):
            submission = await self.create_submission(topic)
            yield submission

    async def create_submission(self, topic: Topic) -> Submission:
        """
        Simulates the generation of a single submission for a given topic by an LLM.

        Args:
            topic (Topic): The topic for which the submission is created.

        Returns:
            Submission: The generated submission.
        """
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        content = f"Generated content by {self.uuid} for topic '{topic.title}'"
        return Submission(topic, self, content)

    async def get_labeling_vote_response(
        self, submission: Submission, vote_schema: dict
    ) -> dict:
        vote_json = json_utils.generate_fake_json(
            vote_schema
        )  # TODO Implement the logic for getting a response from the LLM
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        logging.info(
            f"LLMAgentParticipant {self.uuid} voted with label on submission {submission.uuid}"
        )
        return vote_json

    async def get_comparative_vote_response(
        self, submissions: List[Submission], vote_schema: dict
    ) -> dict:
        vote_json = json_utils.generate_fake_json(
            vote_schema
        )  # TODO Implement the logic for getting a response from the LLM
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        logging.info(
            f"LLMAgentParticipant {self.uuid} voted comparatively on submissions {[submission.uuid for submission in submissions]}"
        )
        return vote_json

    def __str__(self) -> str:
        """
        Provides a string representation of the LLM agent participant.

        Returns:
            str: A string that includes the LLM agent participant's uuid.
        """
        return f"LLMAgentParticipant ID: {self.uuid}"
