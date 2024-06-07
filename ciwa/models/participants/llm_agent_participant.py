# filename: ciwa/models/participants/llm_agent_participant.py

from ciwa.models.participants.participant import Participant
from ciwa.models.topic import Topic
from ciwa.models.submission import Submission
from typing import List, Dict, Any, AsyncGenerator, Optional
import asyncio
import logging
from ciwa.tests.utils import json_utils
from ciwa.utils import prompt_loader
from ciwa.models.schema_factory import SchemaFactory

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

    DEFAULT_MAX_RESPONSE_ATTEMPTS = 3

    def __init__(self, model: str, prompt_template: str, **kwargs):
        """
        Initializes a new instance of LLMAgentParticipant with a unique id.

        """
        super().__init__()
        self.model = model
        self.max_response_attempts = kwargs.get(
            "max_response_attempts", self.DEFAULT_MAX_RESPONSE_ATTEMPTS
        )
        self.prompt_template = prompt_template
        self.prompts = prompt_loader.get_prompts(self.__class__)
        logging.info(
            f"{self.__class__.__name__} initialized with model: {self.model} and prompt_template: {self.prompt_template}"
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
            f"Generating {num_submissions} submissions for topic '{topic.title}' by {self.__class__.__name__} {self.uuid}"
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

        """
        1. get the submission_prompt
        2. get the expected submission response schema
        3. prompt the LLM for a submission using the topic's title and description, submission response schema
        4. check that the response is valid json (against the schemaFactory["submission"] schema)
        5. create a submission object from the json response
        6. return Submission
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
                f"Submission generation failed for {self.__class__.__name__} {self.uuid}."
            )
            return None

        logging.info(f"Submission response received: {submission_response}")
        content = submission_response["submission"]["content"]
        submission = Submission(topic, self, content)
        return submission

    async def send_prompt_with_retries(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        max_attempts: Optional[int] = None,
        attempt: int = 0,
    ) -> Dict[str, Any]:
        max_attempts = max_attempts or self.max_response_attempts
        response = await self.send_prompt(prompt, response_schema)
        response_json = json_utils.get_json(response)
        valid_response = response_json and json_utils.is_valid_json_for_schema(
            response_json, response_schema
        )
        if valid_response:
            return response_json
        else:
            retry_prompt = f"{self.prompts["invalid_json_response"]}\n{prompt}"
            if attempt < max_attempts:
                logging.info(
                    f"Attempt {attempt + 1} of {max_attempts}: Invalid JSON response received from {self.__class__.__name__} {self.uuid}:\n{response}\n Retrying..."
                )
                return await self.send_prompt_with_retries(
                    retry_prompt, response_schema, max_attempts, attempt + 1
                )
            else:
                logging.error(
                    f"Max attempts reached. Invalid JSON response received from {self.__class__.__name__} {self.uuid}."
                )
                return None

    async def send_prompt(
        self, prompt: str, response_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        await asyncio.sleep(SLEEP_DELAY)  # Simulate processing time
        return json_utils.generate_fake_json(response_schema)

    async def _get_vote_response(self, prompt: str, schema: dict) -> dict:
        vote_json = await self.send_prompt_with_retries(prompt, schema)

        if vote_json is None:
            logging.error(
                f"vote generation failed for {self.__class__.__name__} {self.uuid}."
            )
            return None

        logging.info(f"vote response received: {vote_json}")
        return vote_json

    async def get_labeling_vote_response(
        self, submission: Submission, vote_schema: dict
    ) -> dict:
        content = submission.content
        vote_prompt = self.get_labeling_vote_prompt(content)
        vote_json = await self._get_vote_response(vote_prompt, vote_schema)
        logging.info(
            f"{self.__class__.__name__} {self.uuid} voted with label on vote {Submission.uuid}"
        )
        return vote_json

    async def get_comparative_vote_response(
        self, submissions: List[Submission], vote_schema: dict
    ) -> dict:
        content = "\n\n".join(
            [
                f"Submission {index + 1}:\n{submission.content}"
                for index, submission in enumerate(submissions)
            ]
        )
        vote_prompt = self.get_comparative_vote_prompt(content)
        vote_json = await self._get_vote_response(vote_prompt, vote_schema)
        logging.info(
            f"{self.__class__.__name__} {self.uuid} voted comparatively on submissions {[submission.uuid for submission in submissions]}"
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
                "prompt_template": {"type": "string"},
                "type": {
                    "type": "string",
                    "const": f"{self.__class__.__name__}",
                },
            },
            "required": ["uuid", "model", "prompt_template"],
        }

    def get_object_json(self) -> dict:
        """
        Returns a JSON representation of the LLMAgentParticipant object.

        Returns:
            dict: A dictionary representing the LLMAgentParticipant object.
        """
        return {
            "uuid": str(self.uuid),
            "model": self.model,
            "prompt_template": self.prompt_template,
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
        return self.prompts["system_message"].format(
            process_name=process_name, process_description=process_description
        )

    def get_submission_prompt(self, topic_title: str, topic_description: str) -> str:
        return self.prompts["submission_prompt"].format(
            topic_title=topic_title, topic_description=topic_description
        )

    def get_labeling_vote_prompt(self, submission_content: str) -> str:
        return self.prompts["labeling_vote_prompt"].format(
            submission_content=submission_content
        )

    def get_comparative_vote_prompt(self, submissions_contents: str) -> str:
        return self.prompts["comparative_vote_prompt"].format(
            submissions_contents=submissions_contents
        )

    def get_respond_with_json(self, schema: dict) -> str:
        return self.prompts["respond_with_json"].format(schema=schema)
