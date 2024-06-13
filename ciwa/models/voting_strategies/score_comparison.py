# models/voting_strategies/score_comparison.py

from typing import Dict, Any, List
from ciwa.models.voting_strategies.voting_strategy import ComparativeVotingStrategy
from ciwa.models.schema_factory import SchemaFactory
from ciwa.models.voting_results import VotingResults


ROUND_NDIGITS = 3


class ScoreComparison(ComparativeVotingStrategy):

    def __init__(self, start_value: int, end_value: int, increment_value: int = None):
        super().__init__()
        self.start_value = start_value
        self.end_value = end_value
        self.increment_value = increment_value
        self.submission_index_map = {}

    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        results = {}
        total_scores = {submission_id: 0 for submission_id in submission_ids}

        voter_count = 0
        for participant_id, vote_data in voting_results.votes_data.items():
            voter_count += 1
            for submission_i, score in vote_data["vote"].items():
                index = int(submission_i.replace("submission_", ""))
                submission_id = self.submission_index_map[index]
                total_scores[submission_id] += score

        results = {
            submission_id: round(total / voter_count, ROUND_NDIGITS)
            for submission_id, total in sorted(
                total_scores.items(), key=lambda item: item[1]
            )
        }

        return results

    def get_vote_prompt(self, submissions: List["Submission"]) -> str:
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

        self.submission_index_map = {
            i + 1: submissions[i].uuid for i in range(len(submissions))
        }
        return super().get_vote_prompt(submissions, values=values_str)

    def get_vote_schema(self, num_submissions: int) -> Dict[str, Any]:
        return SchemaFactory.create_object_schema(
            "vote",
            {
                "type": "object",
                "properties": {
                    f"submission_{i+1}": {
                        "title": "Score",
                        "description": "The score for this submission.",
                        "type": "integer",
                        "minimum": self.start_value,
                        "maximum": self.end_value,
                    }
                    for i in range(num_submissions)
                },
                "required": [f"submission_{i+1}" for i in range(num_submissions)],
            },
        )
