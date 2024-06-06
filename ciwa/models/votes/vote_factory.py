# filename: ciwa/models/votes/vote_factory.py
from ciwa.models.votes.independent_vote import BinaryVote
from ciwa.models.votes.comparative_vote import RankedVote


class VoteFactory:
    _vote_types = {
        "binary_vote": BinaryVote,
        "ranked_vote": RankedVote,
        # Add other vote types here as needed
    }

    @staticmethod
    def create_vote(vote_type: str, participant: "Participant", **kwargs) -> "Vote":
        """
        Factory method to create a vote of the specified type.

        Args:
            vote_type: The type of vote to create.
            participant: The participant casting the vote.
            kwargs: Additional keyword arguments necessary for initializing the vote.

        Returns:
            An instance of Vote.

        Raises:
            ValueError: If the vote_type is not supported.
        """
        vote_class = VoteFactory._vote_types.get(vote_type)
        if not vote_class:
            raise ValueError(f"Unsupported vote type: {vote_type}")
        return vote_class(participant, **kwargs)
