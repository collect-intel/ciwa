# models/voting_methods/enum_label.py
"""
This module contains the EnumLabel class, a concrete implementation
of the LabelVotingMethod, which applies a label vote based on enumerated values.
"""

from typing import List, Dict, Any
from ciwa.models.voting_methods.voting_method import LabelVotingMethod
from ciwa.utils.json_utils import SchemaFactory
from ciwa.models.voting_results import VotingResults


class EnumLabel(LabelVotingMethod):
    """
    Concrete VotingMethod class that applies a label vote based on enumerated values.
    """

    def __init__(self, enum_values: List[str]):
        super().__init__()
        self.enum_values = enum_values
        self.vote_schema = self.get_vote_schema()

    def process_votes(
        self, voting_results: VotingResults, submission_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Processes a VotingResults object to get an aggregated result.

        Args:
            voting_results (VotingResults): An object holding the voting results.
            submission_ids (List[str]): List of submission.uuid's that were available
                                        for voting. Allows aggregate results to return
                                        empty/none values for submissions that received
                                        no votes.
        Returns:
            Dict[str, Any]: The result of the vote processing, specific to the voting_method.
        """
        # Validate votes against submission_ids (implementation needed)
        results = {
            submission_id: {value: 0 for value in self.enum_values}
            for submission_id in submission_ids
        }
        for submission_id, votes in voting_results.votes_data.items():
            for vote in votes.values():
                results[submission_id][vote["vote"]] += 1
        return results

    def get_vote_schema(self, **kwargs) -> Dict[str, Any]:
        """
        Returns the JSON schema for the vote data.
        """
        vote_structure = {"type": "string", "enum": self.enum_values}
        return SchemaFactory.create_object_schema("vote", vote_structure)

    def __str__(self) -> str:
        return "Enum Label Method"
