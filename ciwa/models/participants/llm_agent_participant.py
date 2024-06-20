# models/participants/llm_agent_participant.py
"""
This module contains the LLMAgentParticipant class, which represents an LLM (Large Language Model)
Agent participant in the system. This class is responsible for generating submissions automatically
based on a given topic.
"""

from typing import List, Dict, Any, AsyncGenerator, Optional
import asyncio
import logging
from ciwa.models.participants.participant import Participant
from ciwa.models.submission import Submission
from ciwa.utils import prompt_loader
from ciwa.tests.utils import json_utils
from ciwa.models.schema_factory import SchemaFactory


# for testing only:
SLEEP_DELAY = 0.0  # seconds to mock LLM API response times


class LLMAgentParticipant(Participant):
    """
    Represents an LLM (Large Language Model) Agent participant in the system.
    This class is responsible for generating submissions automatically based on a given topic.
    """

    DEFAULT_MAX_RESPONSE_ATTEMPTS = 3

    def __init__(self, model: str, **kwargs):
        """
        Initializes a new instance of LLMAgentParticipant with a unique id.
        """
        super().__init__()
        self.model = model
        self.max_response_attempts = kwargs.get(
            "max_response_attempts", self.DEFAULT_MAX_RESPONSE_ATTEMPTS
        )
        self.prompts = prompt_loader.get_prompts(self.__class__)
        logging.info(
            "%s initialized with model: %s", self.__class__.__name__, self.model
        )

    async def generate_submissions(
        self, topic: "Topic", num_submissions: int
    ) -> AsyncGenerator[Submission, None]:
        """
        Asynchronously generates submissions for a given topic, yielding each
        submission as it's created.

        Args:
            topic (Topic): The topic for which submissions are to be generated.
            num_submissions (int): The number of submissions to generate.

        Yields:
            Submission: A submission created for the specified topic.
        """
        logging.info(
            "Generating %d submissions for topic '%s' by %s %s",
            num_submissions,
            topic.title,
            self.__class__.__name__,
            self.uuid,
        )

        tasks = [
            asyncio.create_task(self.create_submission(topic))
            for _ in range(num_submissions)
        ]
        for task in asyncio.as_completed(tasks):
            submission = await task
            if submission:
                yield submission

    async def create_submission(self, topic: "Topic") -> Optional[Submission]:
        """
        Simulates the generation of a single submission for a given topic by an LLM.

        Args:
            topic (Topic): The topic for which the submission is created.

        Returns:
            Submission: The generated submission, or None if generation fails.
        """
        submission_prompt = self.get_submission_prompt(topic.title, topic.description)
        submission_response_schema = SchemaFactory.create_object_schema(
            "submission", Submission.get_response_schema()
        )

        submission_response = await self.send_prompt_with_retries(
            submission_prompt, submission_response_schema
        )

        if submission_response is None:
            logging.error(
                "Submission generation failed for %s %s",
                self.__class__.__name__,
                self.uuid,
            )
            return None

        logging.info("Submission response received: %s", submission_response)
        content = submission_response["submission"]["content"]
        return Submission(topic, self, content)

    async def send_prompt_with_retries(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        max_attempts: Optional[int] = None,
        attempt: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a prompt with retries if the response is invalid.

        Args:
            prompt (str): The prompt to send.
            response_schema (Dict[str, Any]): The schema to validate the response against.
            max_attempts (Optional[int]): The maximum number of attempts.
            attempt (int): The current attempt number.

        Returns:
            Optional[Dict[str, Any]]: The valid response, or None if all attempts fail.
        """
        max_attempts = max_attempts or self.max_response_attempts
        response = await self.send_prompt(prompt, response_schema)
        response_json = json_utils.get_json(response)
        if response_json and json_utils.is_valid_json_for_schema(
            response_json, response_schema
        ):
            return response_json

        retry_prompt = f"{self.prompts['invalid_json_response']}\n{prompt}"
        if attempt < max_attempts:
            logging.info(
                "Attempt %d of %d: Invalid JSON response received from %s %s:\n%s\nRetrying...",
                attempt + 1,
                max_attempts,
                self.__class__.__name__,
                self.uuid,
                response,
            )
            return await self.send_prompt_with_retries(
                retry_prompt, response_schema, max_attempts, attempt + 1
            )

        logging.error(
            "Max attempts reached. Invalid JSON response received from %s %s.",
            self.__class__.__name__,
            self.uuid,
        )
        return None

    async def send_prompt(
        self, prompt: str, response_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulates sending a prompt and getting a response.

        Args:
            prompt (str): The prompt to send.
            response_schema (Dict[str, Any]): The schema to validate the response against.

        Returns:
            Dict[str, Any]: The simulated response.
        """
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        return json_utils.generate_fake_json(response_schema)

    async def _get_vote_response(self, prompt: str, schema: dict) -> dict:
        """
        Gets a vote response with retries if the response is invalid.

        Args:
            prompt (str): The prompt to send.
            schema (dict): The schema to validate the response against.

        Returns:
            dict: The valid response, or an empty dict if all attempts fail.
        """
        vote_json = await self.send_prompt_with_retries(prompt, schema)
        if vote_json is None:
            logging.error(
                "Vote generation failed for %s %s", self.__class__.__name__, self.uuid
            )
            return {}

        logging.info("Vote response received: %s", vote_json)
        return vote_json

    async def get_label_vote_response(
        self, submission: Submission, vote_schema: dict, vote_prompt: str
    ) -> dict:
        """
        Gets a label vote response for a submission.

        Args:
            submission (Submission): The submission to vote on.
            vote_schema (dict): The schema to validate the response against.
            vote_prompt (str): The prompt to send.

        Returns:
            dict: The valid response, or an empty dict if all attempts fail.
        """
        vote_json = await self._get_vote_response(vote_prompt, vote_schema)
        logging.info(
            "%s %s voted with label on submission %s",
            self.__class__.__name__,
            self.uuid,
            submission.uuid,
        )
        return vote_json

    async def get_compare_vote_response(
        self, submissions: List[Submission], vote_schema: dict, vote_prompt: str
    ) -> dict:
        """
        Gets a compare vote response for a list of submissions.

        Args:
            submissions (List[Submission]): The submissions to vote on.
            vote_schema (dict): The schema to validate the response against.
            vote_prompt (str): The prompt to send.

        Returns:
            dict: The valid response, or an empty dict if all attempts fail.
        """
        vote_json = await self._get_vote_response(vote_prompt, vote_schema)
        logging.info(
            "%s %s voted comparely on submissions %s",
            self.__class__.__name__,
            self.uuid,
            [submission.uuid for submission in submissions],
        )
        return vote_json

    @staticmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent an LLMAgentParticipant object's properties.
        """
        return {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "model": {"type": "string"},
                "type": {
                    "type": "string",
                    "const": "LLMAgentParticipant",
                },
            },
            "required": ["uuid", "model"],
        }

    def to_json(self) -> dict:
        """
        Returns a JSON representation of the LLMAgentParticipant object.
        """
        return {
            "uuid": str(self.uuid),
            "model": self.model,
            "type": f"{self.__class__.__name__}",
        }

    def __str__(self) -> str:
        """
        Provides a string representation of the LLM agent participant.

        Returns:
            str: A string that includes the LLM agent participant's uuid.
        """
        return f"{self.__class__.__name__} ID: {self.uuid}"

    def get_system_message(self, process_name: str, process_description: str) -> str:
        """
        Generates a system message based on the provided process name and description.

        Args:
            process_name (str): The name of the process.
            process_description (str): The description of the process.

        Returns:
            str: The formatted system message.
        """
        return self.prompts["system_message"].format(
            process_name=process_name, process_description=process_description
        )

    def get_submission_prompt(self, topic_title: str, topic_description: str) -> str:
        """
        Generates a submission prompt based on the provided topic title and description.

        Args:
            topic_title (str): The title of the topic.
            topic_description (str): The description of the topic.

        Returns:
            str: The formatted submission prompt.
        """
        return self.prompts["submission_prompt"].format(
            topic_title=topic_title, topic_description=topic_description
        )

    def get_respond_with_json(self, schema: dict) -> str:
        """
        Generates a prompt to respond with JSON based on the provided schema.

        Args:
            schema (dict): The schema to include in the prompt.

        Returns:
            str: The formatted respond with JSON prompt.
        """
        return self.prompts["respond_with_json"].format(schema=schema)
