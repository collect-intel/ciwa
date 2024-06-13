# models/voting_methods/yes_no_label.py

from typing import Dict, Any
from ciwa.models.voting_methods.enum_label import EnumLabel


class YesNoLabel(EnumLabel):
    """
    Concrete VotingMethod class that applies a label vote of "yes" or "no".
    """

    def __init__(self):
        super().__init__(enum_values=["yes", "no"])
