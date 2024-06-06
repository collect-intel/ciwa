# filename: ciwa/models/votes/comparative_vote.py

from abc import ABC
from ciwa.models.votes.vote import Vote
from typing import Any, List


class ComparativeVote(Vote, ABC):
    """
    Abstract class representing a vote on a set of Submissions by comparing them to each other.
    """

    pass


class RankedVote(ComparativeVote):
    """
    Concrete implementation of a ranked vote, where the vote is an ordered list of Submissions.

    Attributes:
        rankings (List[Submission]): The list of Submissions in order from first to last as ranked by the participant.

    """

    def __init__(
        self, participant: "Participant", rankings: List["Submission"]
    ) -> None:
        """
        Initializes a new instance of RankedVote with the participant and a list of Submissions.

        Args:
            participant (Participant): The participant casting the vote.
            rankings (List[Submission]): The list of Submissions as ranked by the participant.
        """
        super().__init__(participant)
        self.rankings = rankings

    def get_value(self) -> List["Submission"]:
        """
        Returns the ordered list of Submissions as ranked by the participant.
        """
        return self.rankings

    def __str__(self) -> str:
        """
        Provides a string representation of the ranked vote, indicating the participant and the rankings.
        """
        ranking_descriptions = [
            f"{i + 1}. {submission}" for i, submission in enumerate(self.rankings)
        ]
        return (
            f"Ranked Vote by {self.participant.uuid} at {self.created_at}: \n"
            + "\n".join(ranking_descriptions)
        )
