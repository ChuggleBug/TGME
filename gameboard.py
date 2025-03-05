
from __future__ import annotations
from typing import TYPE_CHECKING

from typing import NamedTuple
from structures import Matrix

if TYPE_CHECKING:
    from typing import List, Set, Union, Optional, Tuple, Iterable
    from button_controller import DirectionButton, ActionButton
    from rules import TileMatchRule, TileGeneratorRule, UserInputRule


class Coordinate(NamedTuple):
    x: int
    y: int

class UserInputRuleSet(NamedTuple):
    input_rule: UserInputRule
    input_set: Set[DirectionButton | ActionButton]

class GameElement:
    pass


class TileElement:
    def __init__(self):
        self._elements: List[GameElement] = []


class ElementSet:
    def __init__(self):
        self._elements: List[Tuple[GameElement, Coordinate]] = []

    def add_element(self, element: GameElement, coordinate: Coordinate):
        self._elements.append((element, coordinate))

    def get_elements(self) -> List[Tuple[GameElement, Coordinate]]:
        return self._elements


class Board:
    def __init__(self, *, rows: int, cols: int):
        self._tiles: Matrix[TileElement] = Matrix(rows=rows, cols=cols, initializer=lambda: TileElement())
        self._match_rule: Optional[TileMatchRule] = None
        self._generator_rule: Optional[TileGeneratorRule] = None
        self._live_tiles: Optional[ElementSet] = None
        self._input_rules: List[UserInputRuleSet] = []

    def get_live_tiles(self) -> Optional[ElementSet]:
        return self._live_tiles

    # This function is sure to exist
    def set_tile_match_rule(self, match_rule: TileMatchRule):
        self._match_rule = match_rule

    # This one might be subject to change
    def set_tile_generator_rule(self, generator_rule: TileGeneratorRule):
        self._generator_rule = generator_rule

    def add_user_input_rule(self, input_rule: UserInputRule, input_set: Set[DirectionButton | ActionButton]):
        self._input_rules.append(UserInputRuleSet(input_rule, input_set))

    def get_user_input_rules(self) -> Iterable[UserInputRuleSet]:
        return self._input_rules

    def update(self) -> None:
        """
        update the game after a single tick has passed
        """
        match_found = False
        generated_tile: Optional[ElementSet] = None
        if self._match_rule is not None:
            match_found = self._match_rule.check_matches(self)
        if self._generator_rule is not None:
            generated_tile = self._generator_rule.produce_tiles(self)
