# models/voting_strategies/ranking_comparison.py

from typing import Dict, Any, List
from ciwa.models.voting_strategies.voting_strategy import ComparativeVotingStrategy
from ciwa.models.schema_factory import SchemaFactory
from ciwa.models.voting_results import VotingResults


ROUND_NDIGITS = 3


class RankingComparison(ComparativeVotingStrategy):

    def __init__(self):
        super().__init__()
        self.submission_index_map = {}

    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Processes the ranking votes to get an aggregated result, in the form of
        an average ranking from the ranking given by each Participant to each submission.

        Args:
            voting_results (VotingResults): An object holding the voting results.
        Returns:
            Dict[str, Any]: The aggregated result of the votes.
        """
        results = {}
        total_scores = {submission_id: 0 for submission_id in submission_ids}

        voter_count = 0
        for participant_id, vote_data in voting_results.votes_data.items():
            voter_count += 1
            for rank, index in enumerate(vote_data["vote"]):
                submission_id = self.submission_index_map[index]
                total_scores[submission_id] += rank

        results = {
            submission_id: round(total / voter_count, ROUND_NDIGITS)
            for submission_id, total in sorted(
                total_scores.items(), key=lambda item: item[1]
            )
        }

        return results

    def get_vote_prompt(self, submissions: List["Submission"]) -> str:
        """
        Generates a prompt for ranking the submissions based on their contents and
        creates a mapping from indices to submission IDs.

        Args:
            submissions (List[Submission]): The submissions.

        Returns:
            str: The generated prompt for ranking.
        """
        self.submission_index_map = {
            i + 1: submissions[i].uuid for i in range(len(submissions))
        }
        return super().get_vote_prompt(submissions)

    def get_vote_schema(self, num_submissions: int) -> Dict[str, Any]:
        """
        Returns the schema for validating the rankings.

        Returns:
            Dict[str, Any]: The schema for validating the rankings.
        """
        vote_structure = {
            "type": "array",
            "title": "List of Unique Integers",
            "description": f"A list of unique integers in the range from 1 to {num_submissions}",
            "uniqueItems": True,
            "items": {"type": "integer", "minimum": 1, "maximum": num_submissions},
            "additionalItems": False,
            "maxItems": num_submissions,
            "minItems": num_submissions,
        }
        return SchemaFactory.create_object_schema("vote", vote_structure)

    def __str__(self) -> str:
        return "Ranking Comparison Strategy"
