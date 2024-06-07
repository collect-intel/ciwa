# filename: ciwa/models/voting_strategies/yes_no_labeling.py

from typing import List, Dict, Any
from ciwa.models.voting_strategies.enum_labeling import EnumLabeling


class YesNoLabeling(EnumLabeling):
    """
    Concrete VotingStrategy class that applies a label vote of "yes" or "no".
    """

    def __init__(self):
        enum_values = ["yes", "no"]
        super().__init__(enum_values)
