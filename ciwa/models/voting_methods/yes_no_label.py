# models/voting_methods/yes_no_label.py
"""
This module contains the YesNoLabel class, a concrete implementation
of the EnumLabel voting method, which applies a label vote of "yes" or "no".
"""

from ciwa.models.voting_methods.enum_label import EnumLabel


class YesNoLabel(EnumLabel):
    """
    Concrete VotingMethod class that applies a label vote of "yes" or "no".
    """

    def __init__(self):
        super().__init__(enum_values=["yes", "no"])
