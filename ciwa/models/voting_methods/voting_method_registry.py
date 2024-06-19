# models/voting_methods/voting_method_registry.py

"""
This registry allows for VotingMethods to be recognized by the VotingManagerFactory using
a simple decorator:

@register_voting_method
class NameOfVotingMethod(VotingMethod):
    ...
"""

from typing import Type, Dict
from ciwa.models.voting_methods.voting_method import VotingMethod

_voting_method_registry: Dict[str, Type[VotingMethod]] = {}


def register_voting_method(voting_method: Type[VotingMethod]) -> Type[VotingMethod]:
    """
    Register a voting method class in the global registry.

    Args:
        voting_method (Type[VotingMethod]): The voting method class to register.

    Returns:
        Type[VotingMethod]: The registered voting method class.
    """
    _voting_method_registry[voting_method.__name__] = voting_method
    return voting_method


def get_voting_method(voting_method_name: str) -> Type[VotingMethod]:
    """
    Get a voting method class from the global registry by its name.

    Args:
        voting_method_name (str): The name of the voting method.

    Returns:
        Type[VotingMethod]: The voting method class.
    """
    if voting_method_name not in _voting_method_registry:
        raise ValueError(f"Voting method {voting_method_name} is not registered.")
    return _voting_method_registry[voting_method_name]
