# models/voting_methods/score_label.py

from typing import List, Dict, Any
from ciwa.models.voting_methods.voting_method import LabelVotingMethod
from ciwa.models.schema_factory import SchemaFactory
from ciwa.models.voting_results import VotingResults

ROUND_NDIGITS = 3


class ScoreLabel(LabelVotingMethod):

    def __init__(self, start_value: int, end_value: int, increment_value: int = None):
        super().__init__()
        self.start_value = start_value
        self.end_value = end_value
        self.increment_value = increment_value

    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
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

    def get_vote_prompt(self, submission: "Submission") -> str:
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

        return super().get_vote_prompt(submission, values=values_str)

    def get_vote_schema(self) -> Dict[str, Any]:
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
