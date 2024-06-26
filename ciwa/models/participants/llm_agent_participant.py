# models/participants/llm_agent_participant.py
"""
This module contains the LLMAgentParticipant class, which represents an LLM (Large Language Model)
Agent participant in the system. This class is responsible for generating submissions automatically
based on a given topic.
"""

from typing import List, Dict, Any, AsyncGenerator, Optional, Callable
import asyncio
import logging
from ciwa.models.participants.participant import Participant
from ciwa.models.submission import Submission
from ciwa.utils import prompt_loader
from ciwa.utils import json_utils
from ciwa.utils.json_utils import SchemaFactory


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
        Generates a single submission for a given topic by an LLM.

        Args:
            topic (Topic): The topic for which the submission is created.

        Returns:
            Submission: The generated submission, or None if generation fails.
        """
        submission_prompt = self.get_submission_prompt(topic.title, topic.description)
        submission_response_schema = self._get_submission_response_schema(topic)
        # Use the _get_submission_response method
        submission_response = await self._get_submission_response(
            prompt=submission_prompt,
            schema=submission_response_schema,
            validator=topic.submission_validator,
            invalid_message=topic.submission_invalid_message,
        )

        if not submission_response:
            logging.error(
                "Submission generation failed for %s %s",
                self.__class__.__name__,
                self.uuid,
            )
            return None

        logging.info("Submission response received: %s", submission_response)
        content = submission_response["submission"]["content"]
        return Submission(topic, self, content)

    def _get_submission_response_schema(self, topic: "Topic") -> dict:
        """
        Returns the JSON schema for a submission response.
        """
        return SchemaFactory.create_object_schema(
            "submission",
            Submission.get_response_schema(topic.submission_content_schema),
        )

    def _get_batch_submissions_response_schema(
        self, num_submissions: int, topic: "Topic"
    ) -> dict:
        """
        Returns the JSON schema for a batch submission response.
        """
        return SchemaFactory.create_object_schema(
            "submissions",
            Submission.get_batch_submissions_schema(
                num_submissions=num_submissions,
                content_schema=topic.submission_content_schema,
            ),
        )

    async def create_batch_submissions(
        self, topic: "Topic", max_subs_per_topic: int
    ) -> List[Submission]:
        """
        Generates a batch of submissions for a given topic by an LLM.
        """

        prompt = self.prompts["batch_submissions_prompt"].format(
            topic_title=topic.title,
            topic_description=topic.description,
            max_subs_per_topic=max_subs_per_topic,
        )

        submissions_response = await self._get_submission_response(
            prompt=prompt,
            schema=self._get_batch_submissions_response_schema(
                num_submissions=max_subs_per_topic, topic=topic
            ),
            validator=topic.submission_validator,
            invalid_message=topic.submission_invalid_message,
        )

        submissions = submissions_response.get("submissions", [])
        try:
            return [Submission(topic, self, item["content"]) for item in submissions]
        except:
            import pdb

            pdb.set_trace()

    async def _get_submission_response(
        self,
        prompt: str,
        schema: dict,
        validator: Callable[[Any], bool],
        invalid_message: str,
    ) -> dict:
        """
        Gets a submission response with retries if the response is invalid.

        Args:
            prompt (str): The prompt to send.
            schema (dict): The schema to validate the response against.
            validator (Callable[[Any], bool]): The function to validate the submission.
            invalid_message (str): The message to display if the submission is invalid.

        Returns:
            dict: The valid response, or an empty dict if all attempts fail.
        """
        validation_steps = [
            (self._validate_json_schema(schema), self.prompts["invalid_json_response"]),
            (validator, invalid_message),
        ]
        submission_json = await self.send_prompt_with_retries(
            prompt=prompt, response_schema=schema, validation_steps=validation_steps
        )
        if submission_json is None:
            logging.error(
                "Submission generation failed for %s %s",
                self.__class__.__name__,
                self.uuid,
            )
            return {}
        return submission_json

    def _validate_json_schema(self, schema: dict) -> Callable[[Any], bool]:
        """
        Returns a validator function that validates a response against a given JSON schema.

        Args:
            schema (dict): The JSON schema to validate against.

        Returns:
            Callable[[Any], bool]: The validator function.
        """

        def validator(response: Any) -> bool:
            return json_utils.is_valid_json_for_schema(response, schema)

        return validator

    async def send_prompt_with_retries(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        validation_steps: List[tuple[Callable[[Any], bool], str]],
        max_attempts: Optional[int] = None,
        attempt: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a prompt with retries if the response is invalid based on the provided
        validation steps.

        Args:
            prompt (str): The prompt to send.
            response_schema (Dict[str, Any]): The schema to validate the response against.
            validation_steps (List[tuple[Callable[[Any], bool], str]]): List of tuples
                containing validator functions and their corresponding invalid messages.
            max_attempts (Optional[int]): The maximum number of attempts.
            attempt (int): The current attempt number.

        Returns:
            Optional[Dict[str, Any]]: The valid response, or None if all attempts fail.
        """
        max_attempts = max_attempts or self.max_response_attempts
        response = await self.send_prompt(prompt, response_schema)
        response_json = json_utils.get_json(response)

        for validator, invalid_message in validation_steps:
            if not validator(response_json):
                retry_prompt = f"{invalid_message}\n{prompt}"
                if attempt < max_attempts:
                    logging.info(
                        "Attempt %d of %d: Invalid response received from %s %s:\n%s\nRetrying...",
                        attempt + 1,
                        max_attempts,
                        self.__class__.__name__,
                        self.uuid,
                        response,
                    )
                    return await self.send_prompt_with_retries(
                        prompt=retry_prompt,
                        response_schema=response_schema,
                        validation_steps=validation_steps,
                        max_attempts=max_attempts,
                        attempt=attempt + 1,
                    )
                logging.error(
                    "Max attempts reached. Invalid response received from %s %s.",
                    self.__class__.__name__,
                    self.uuid,
                )
                return None
        return response_json

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
        response_schema_string = json_utils.get_json_string(response_schema)
        prompt += f"\n{self.get_respond_with_json(response_schema_string)}"
        logging.info(
            "Sending prompt to %s %s: %s", self.__class__.__name__, self.uuid, prompt
        )
        response = await self._send_prompt(prompt)
        return response

    async def _send_prompt(self, prompt: str) -> str:
        """
        Method to be implemented by subclasses to send the prepared prompt to the LLM model.

        By default, this method will sleep for a short time to simulate processing, and
        return random JSON data based on the provided schema. Subclasses should override
        this method to send the prompt to the LLM model and return the actual response.
        """
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        response_schema = json_utils.extract_json_schema(prompt)
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
        validation_steps = [
            (self._validate_json_schema(schema), self.prompts["invalid_json_response"]),
        ]
        vote_json = await self.send_prompt_with_retries(
            prompt=prompt, response_schema=schema, validation_steps=validation_steps
        )
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
