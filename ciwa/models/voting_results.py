# models/voting_results.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import datetime


class VotingResults(ABC):
    """
    Abstract base class to hold and manage voting results.

    Attributes:
        participants (List[str]): List of participant IDs who voted.
        votes_data (Dict[str, Any]): Raw vote data from each participant.
        aggregated_results (Dict[str, Any]): Aggregated results of all participant votes.
    """

    def __init__(self) -> None:
        self.participants: List[str] = []
        self.votes_data: Dict[str, Any] = {}
        self.aggregated_results: Dict[str, Any] = {}

    @abstractmethod
    def add_vote(self, participant_id: str, vote_data: Any) -> None:
        """
        Add a participant's vote to the results.

        Args:
            participant_id (str): The ID of the participant who voted.
            vote_data (Any): The raw vote data from the participant.
        """
        pass

    @abstractmethod
    def process_votes(
        self, voting_method: "VotingMethod", submission_ids: List[str]
    ) -> None:
        """
        Process the raw votes using the provided voting voting_method to produce aggregated results.
                Requires list of submission.uuid's to validate votes against and account for any submissions
                that didn't receive any votes.

        Args:
            voting_method (VotingMethod): The voting voting_method to use for processing votes.
            submission_ids (List[str]): List of submission.uuid's that were available for voting on.
        """
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """
        Return a JSON-compatible representation of the voting results.

        Returns:
            Dict[str, Any]: JSON-compatible representation of the voting results.
        """
        pass


class LabelVotingResults(VotingResults):
    """
    Concrete class to hold and manage label voting results.

    Attributes:
        submissions (Dict[str, List[Dict[str, Any]]]):
            Dict of key: submission.uuid, value: List of Dicts: (uuid: participant.uuid, vote: vote_json)
    """

    def __init__(self) -> None:
        super().__init__()
        self.submissions: Dict[str, List[Dict[str, Any]]] = {}

    def add_vote(self, participant_id: str, vote_data: Dict[str, Any]) -> None:
        """
        Add a participant's label vote to the results.

        Args:
            participant_id (str): The ID of the participant who voted.
            vote_data (Dict[str, Any]): The raw vote data from the participant.
        """
        created_at = datetime.datetime.now()
        if participant_id not in self.participants:
            self.participants.append(participant_id)
        for submission_id, vote in vote_data.items():
            vote["created_at"] = created_at
            if submission_id not in self.submissions:
                self.submissions[submission_id] = []
            self.submissions[submission_id].append(
                {"uuid": participant_id, "vote": vote}
            )
            if submission_id not in self.votes_data:
                self.votes_data[submission_id] = {}
            self.votes_data[submission_id][participant_id] = vote

    def process_votes(
        self, voting_method: "LabelVotingMethod", submission_ids: List[str]
    ) -> None:
        """
        Process the raw votes using the provided label voting voting_method to produce aggregated results.

        Args:
            voting_method (LabelVotingMethod): The voting voting_method to use for processing votes.
            submission_ids (List[str]): List of submission.uuid's made available for voting.
        """
        self.aggregated_results = voting_method.process_votes(self, submission_ids)

    def to_json(self) -> Dict[str, Any]:
        """
        Return a JSON-compatible representation of the label voting results.

        Returns:
            Dict[str, Any]: JSON-compatible representation of the label voting results.
        """
        return {
            "submissions": [
                {
                    "uuid": submission_id,
                    "voting_participants": [
                        {
                            "uuid": participant["uuid"],
                            "vote": {
                                "created_at": participant["vote"][
                                    "created_at"
                                ].isoformat(),
                                "vote": participant["vote"]["vote"],
                            },
                        }
                        for participant in voting_participants
                    ],
                }
                for submission_id, voting_participants in self.submissions.items()
            ],
            "aggregated_results": {
                "submissions": [
                    {"uuid": submission_id, "result": result}
                    for submission_id, result in self.aggregated_results.items()
                ]
            },
        }


class CompareVotingResults(VotingResults):
    """
    Concrete class to hold and manage compare voting results.

    Attributes:
        submissions (List[str]): List of submission IDs voted on.
    """

    def __init__(self) -> None:
        super().__init__()

    def add_vote(self, participant_id: str, vote_data: Any) -> None:
        """
        Add a participant's compare vote to the results.

        Args:
            participant_id (str): The ID of the participant who voted.
            vote_data (Any): The raw vote data from the participant.
        """
        vote_data["created_at"] = datetime.datetime.now()
        if participant_id not in self.participants:
            self.participants.append(participant_id)
        self.votes_data[participant_id] = vote_data

    def process_votes(
        self, voting_method: "CompareVotingMethod", submission_ids: List[str]
    ) -> None:
        """
        Process the raw votes using the provided compare voting voting_method to produce aggregated results.

        Args:
            voting_method (CompareVotingMethod): The voting voting_method to use for processing votes.
            submission_ids (List[str]): List of submission.uuid's made available for voting.
        """
        self.aggregated_results = voting_method.process_votes(self, submission_ids)

    def to_json(self) -> Dict[str, Any]:
        """
        Return a JSON-compatible representation of the compare voting results.

        Returns:
            Dict[str, Any]: JSON-compatible representation of the compare voting results.
        """
        return {
            "voting_participants": [
                {
                    "uuid": participant_id,
                    "vote": {
                        "created_at": vote_data["created_at"].isoformat(),
                        "vote": vote_data["vote"],
                    },
                }
                for participant_id, vote_data in self.votes_data.items()
            ],
            "aggregated_results": {
                "submissions": [
                    {"uuid": submission_id, "result": result}
                    for submission_id, result in self.aggregated_results.items()
                ]
            },
        }
