# models/voting_strategies/enum_labeling.py

from typing import List, Dict, Any
from ciwa.models.voting_strategies.voting_strategy import LabelingStrategy
from ciwa.models.schema_factory import SchemaFactory
from ciwa.models.voting_results import VotingResults


class EnumLabeling(LabelingStrategy):
    def __init__(self, enum_values: List[str]):
        super().__init__()
        self.enum_values = enum_values
        self.vote_schema = self.get_vote_schema()

    # TODO validate votes against submission_ids
    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        results = {
            submission_id: {value: 0 for value in self.enum_values}
            for submission_id in submission_ids
        }
        for submission_id, votes in voting_results.votes_data.items():
            for vote in votes.values():
                results[submission_id][vote["vote"]] += 1
        return results

    def get_vote_schema(self) -> Dict[str, Any]:
        vote_structure = {"type": "string", "enum": self.enum_values}
        return SchemaFactory.create_object_schema("vote", vote_structure)

    def __str__(self) -> str:
        return "Enum Labeling Strategy"
