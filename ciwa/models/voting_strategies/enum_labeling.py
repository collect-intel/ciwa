# filename: ciwa/models/voting_strategies/enum_labeling.py

from typing import List, Dict, Any
from ciwa.models.voting_strategies.voting_strategy import LabelingStrategy
from ciwa.models.schema_factory import SchemaFactory


class EnumLabeling(LabelingStrategy):
    def __init__(self, enum_values):
        self.enum_values = enum_values
        self.vote_schema = self.get_vote_schema()

    def process_votes(self, participant_votes_data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for participant_id, data in participant_votes_data.items():
            for submission_id, vote in data["submissions"].items():
                if submission_id not in results:
                    results[submission_id] = {value: 0 for value in self.enum_values}
                results[submission_id][vote["vote"]] += 1
        return results

    @staticmethod
    def get_vote_type() -> str:
        return "enum_vote"

    def get_vote_schema(self) -> Dict[str, Any]:
        vote_structure = {"type": "string", "enum": self.enum_values}
        schema = SchemaFactory.create_object_schema("vote", vote_structure)
        return schema

    def __str__(self) -> str:
        return "Enum Labeling Strategy"
