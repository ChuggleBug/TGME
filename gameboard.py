
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC
from dataclasses import dataclass, field

from typing import NamedTuple
from structures import Matrix
from constants import Color

if TYPE_CHECKING:
    from typing import List, Set, Optional, Tuple, Iterable
    from button_controller import DirectionButton, ActionButton
    from rules import TileMatchRule, TileGeneratorRule, UserInputRule


class Coordinate(NamedTuple):
    x: int
    y: int

class UserInputRuleSet(NamedTuple):
    input_rule: UserInputRule
    input_set: Set[DirectionButton | ActionButton]

@dataclass
class GameElement(ABC):
    """
    The Basic framework for every single game element to inherit from.
    Provides basic data utilities which can be useful for any kind of
    game alongside default values which tend to be common for elements.
    While game elements might have support for a variety of attributes,
    in a single instance of a complete game, not every single attribute
    will be used
    """
    # Elements can spawn on top of this element
    supports_tile_spawn: bool = field(default=False)
    # This element's color has a meaning
    supports_color: bool = field(default=True)
    # The element's color. Only useful if supports_color is True
    element_color: Color = field(default=Color.WHITE)


class TileElement:
    def __init__(self):
        self._elements: List[GameElement] = []

    def can_support_tile_spawn(self):
        """
        Indicates that a tile can have a new element spawned inside of it
        """
        return all(map(lambda e: e.supports_tile_spawn, self._elements))

    def add_game_element(self, element: GameElement):
        self._elements.append(element)


class ElementSet(ABC):
    def __init__(self):
        self._elements: List[Tuple[GameElement, Coordinate]] = []

    def add_element(self, element: GameElement, coordinate: Coordinate):
        self._elements.append((element, coordinate))

    def get_elements(self) -> List[Tuple[GameElement, Coordinate]]:
        return self._elements

    def has_elements(self) -> bool:
        return len(self._elements) > 0

class BoardElementSet(ElementSet):
    def as_relative_coordinates(self) -> RelativeElementSet:
        ...

class RelativeElementSet(ElementSet):
    def as_board_coordinates(self, board: Board, coordinate: Coordinate) -> BoardElementSet:
        """
        Converts the coordinates of element relative to itself to the coordinates
        as if it was on the board at a specified coordinate
        :param board:
        :param coordinate:
        :return: Coordinates of the element set relative to the board
        """
        converted_set = BoardElementSet()
        for element in self.get_elements():
            converted_coords = Coordinate(coordinate.x + element[1].x, coordinate.y + element[1].y)
            if converted_coords.x > board.get_num_columns() or converted_coords.y > board.get_num_rows():
                raise ValueError(f"{converted_coords} have elements outside of the bounds of the board")
            converted_set.add_element(element[0], converted_coords)

        return converted_set

    def get_width(self) -> int:
        left_x = min(map(lambda t: t[1].x, self._elements))
        right_x = min(map(lambda t: t[1].x, self._elements))
        return left_x - right_x + 1

    def get_height(self) -> int:
        top_y = min(map(lambda t: t[1].y, self._elements))
        bottom_y = min(map(lambda t: t[1].y, self._elements))
        return bottom_y - top_y + 1


class Board:
    def __init__(self, rows: int, cols: int, player_id: int):
        self._tiles: Matrix[TileElement] = Matrix(rows=rows, cols=cols, initializer=lambda: TileElement())
        self._match_rule: Optional[TileMatchRule] = None
        self._generator_rule: Optional[TileGeneratorRule] = None
        self._live_tiles: Optional[ElementSet] = None
        self._input_rules: List[UserInputRuleSet] = []
        self._player_id = player_id

    def get_player_id(self):
       return self._player_id

    def get_live_tiles(self) -> Optional[BoardElementSet]:
        return self._live_tiles

    def set_live_tile(self, live_tiles: BoardElementSet):
        self._live_tiles = live_tiles

    def has_live_tiles(self) -> bool:
        return self._live_tiles is not None

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

    def get_num_rows(self) -> int:
        return self._tiles.rows

    def get_num_columns(self) -> int:
        return self._tiles.cols

    def get_tile_at(self, row: int, col: int) -> TileElement:
        return self._tiles.get_mutable(row, col)

    def update(self) -> None:
        """
        update the game after a single tick has passed
        """
        match_found = False
        generated_tile: Optional[BoardElementSet] = None
        if self._match_rule is not None:
            match_found = self._match_rule.check_matches(self)
        if self._generator_rule is not None:
            generated_tile = self._generator_rule.produce_tiles(self)

    def spawn_tiles(self):
        if self._generator_rule:
            generated_tiles = self._generator_rule.produce_tiles(self)
            if generated_tiles:
                print(f"Generated {len(generated_tiles.get_elements())} tiles")
