# models/voting_methods/__init__.py

from ciwa.models.voting_methods.enum_label import EnumLabel
from ciwa.models.voting_methods.yes_no_label import YesNoLabel
from ciwa.models.voting_methods.ranking_compare import RankingCompare
from ciwa.models.voting_methods.score_label import ScoreLabel
from ciwa.models.voting_methods.score_compare import ScoreCompare
from ciwa.models.voting_methods.voting_method_registry import register_voting_method

# Register all voting methods
register_voting_method(EnumLabel)
register_voting_method(YesNoLabel)
register_voting_method(RankingCompare)
register_voting_method(ScoreLabel)
register_voting_method(ScoreCompare)
