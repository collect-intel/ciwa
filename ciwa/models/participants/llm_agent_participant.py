# filename: ciwa/models/participants/llm_agent_participant.py

from ciwa.models.participants.participant import Participant
from ciwa.models.topic import Topic
from ciwa.models.submission import Submission
from ciwa.models.votes.comparative_vote import (
    RankedVote,
)  # TODO: Architect such that we don't need to import this
from ciwa.models.votes.independent_vote import (
    BinaryVote,
)  # TODO: Architect such that we don't need to import this
from typing import List, AsyncGenerator
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
        await asyncio.sleep(1)  # Simulate processing time
        content = f"Generated content by {self.uuid} for topic '{topic.title}'"
        return Submission(topic, self, content)

    # TODO Possibly refactor or delete this method
    # TODO figure out how to architect to not return a BinaryVote every time
    async def generate_independent_vote(self, submission: Submission) -> BinaryVote:
        vote_value = True  # Implement the logic for determining the vote value
        return BinaryVote(participant=self, vote_value=vote_value)

    # TODO Possibly refactor or delete this method
    # TODO figure out how to architect to not return a RankedVote every time
    async def generate_comparative_vote(
        self, submissions: List[Submission]
    ) -> RankedVote:
        rankings = []  # Implement the logic for determining the rankings
        return RankedVote(participant=self, rankings=rankings)

    def __str__(self) -> str:
        """
        Provides a string representation of the LLM agent participant.

        Returns:
            str: A string that includes the LLM agent participant's uuid.
        """
        return f"LLMAgentParticipant ID: {self.uuid}"
