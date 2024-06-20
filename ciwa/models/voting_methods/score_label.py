# models/voting_methods/score_label.py
"""
This module contains the ScoreLabel class, a concrete implementation
of the LabelVotingMethod, which aggregates scores assigned to individual submissions.
"""

from typing import List, Dict, Any
from ciwa.models.voting_methods.voting_method import LabelVotingMethod
from ciwa.models.schema_factory import SchemaFactory
from ciwa.models.voting_results import VotingResults

ROUND_NDIGITS = 3


class ScoreLabel(LabelVotingMethod):
    """
    Concrete VotingMethod class that aggregates scores assigned to individual submissions.
    """

    def __init__(self, start_value: int, end_value: int, increment_value: int = None):
        super().__init__()
        self.start_value = start_value
        self.end_value = end_value
        self.increment_value = increment_value

    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Processes the scores to get an aggregated result.

        Args:
            voting_results (VotingResults): An object holding the voting results.
        Returns:
            Dict[str, Any]: The aggregated result of the votes.
        """
        aggregated_results = {}
        for submission_id in submission_ids:
            scores = [
                vote["vote"]
                for vote in voting_results.votes_data.get(submission_id, {}).values()
            ]
            aggregated_results[submission_id] = {
                "average_score": (
                    round(sum(scores) / len(scores), ROUND_NDIGITS) if scores else None
                )
            }
        return aggregated_results

    def get_vote_prompt(self, submission: "Submission", **kwargs) -> str:
        """
        Generates a prompt for scoring the submission based on its content.

        Args:
            submission (Submission): The submission.

        Returns:
            str: The generated prompt for scoring.
        """
        if self.increment_value:
            values = [
                str(v)
                for v in range(
                    self.start_value, self.end_value + 1, self.increment_value
                )
            ]
            values_str = ", ".join(values)
        else:
            values_str = f"{str(self.start_value)} to {str(self.end_value)}"

        return super().get_vote_prompt(submission, values=values_str, **kwargs)

    def get_vote_schema(self, **kwargs) -> Dict[str, Any]:
        """
        Returns the schema for validating the scores.

        Returns:
            Dict[str, Any]: The schema for validating the scores.
        """
        return SchemaFactory.create_object_schema(
            "vote",
            {
                "title": "Score",
                "description": "The score for this submission.",
                "type": "integer",
                "minimum": self.start_value,
                "maximum": self.end_value,
            },
        )
