from board import Board
from rules import GameConditionRule, NoMoreMatchesPossibleException


class CheckIfMatchPossibleRule(GameConditionRule):
    def check_game_condition(self, board: Board):
        # Algorithm was too complex so this was not done
        pass