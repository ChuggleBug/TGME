
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC
from dataclasses import dataclass, field

from typing import NamedTuple
from structures import Matrix
from constants import Color

if TYPE_CHECKING:
    from typing import List, Set, Optional, Tuple, Iterable, Any
    from button_controller import DirectionButton, ActionButton
    from rules import *

@dataclass
class Coordinate:
    x: int
    y: int

    def __add__(self, other: Any) -> Coordinate:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return Coordinate(self.x + other.x, self.y + other.y)

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
    # Name of the element (useful for debugging sometimes)
    element_name: str = field(default='GameElementDefault')
    # Elements can spawn on top of this element
    supports_tile_spawn: bool = field(default=False)
    # This element's color has a meaning
    supports_color: bool = field(default=True)
    # The element's color. Only useful if supports_color is True
    element_color: Color = field(default=Color.DEFAULT)
    # A single element can move around and is not locked to the tile
    support_tile_move: bool = field(default=True)


class TileElement:
    def __init__(self):
        self._elements: List[GameElement] = []

    def can_support_tile_spawn(self):
        """
        Indicates that a tile can have a new element spawned inside of it
        """
        return all(map(lambda e: e.supports_tile_spawn, self._elements))

    def can_support_move(self):
        """
        Indicates that has the capability to move. Tiles typically are blocked
        from moving by
        """
        return all(map(lambda e: e.support_tile_move, self._elements))

    def add_game_element(self, element: GameElement):
        self._elements.append(element)

    def has_elements(self) -> bool:
        return len(self._elements) > 0

    def __repr__(self):
        return f"TileElement(size={len(self._elements)}, contents={self._elements})"

@dataclass(kw_only=True)
class ElementPair:
    """
    Intermediary class for ElementSet classes
    """
    coordinate: Coordinate
    element: GameElement


class ElementSet(ABC):
    def __init__(self):
        self._elements: List[ElementPair] = []

    def add_element(self, element: GameElement, coordinate: Coordinate):
        self._elements.append(ElementPair(element=element, coordinate=coordinate))

    def get_element_pairs(self) -> List[ElementPair]:
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
        for pair in self.get_element_pairs():
            converted_coords = pair.coordinate + coordinate
            if converted_coords.x > board.get_width() or converted_coords.y > board.get_height():
                raise ValueError(f"{converted_coords} have elements outside of the bounds of the board [(0-0),({board.get_width()},{board.get_height()})]")
            converted_set.add_element(pair.element, converted_coords)

        return converted_set

    def get_width(self) -> int:
        left_x = min(map(lambda t: t.coordinate.x, self._elements))
        right_x = min(map(lambda t: t.coordinate.x, self._elements))
        return left_x - right_x + 1

    def get_height(self) -> int:
        top_y = min(map(lambda t: t.coordinate.y, self._elements))
        bottom_y = min(map(lambda t: t.coordinate.y, self._elements))
        return bottom_y - top_y + 1


class Board:
    def __init__(self, height: int, width: int, player_id: int):
        self._tiles: Matrix[TileElement] = Matrix(rows=height, cols=width, initializer=lambda: TileElement())
        self._match_rule: Optional[TileMatchRule] = None
        self._generator_rule: Optional[TileGeneratorRule] = None
        self._live_tiles: Optional[ElementSet] = None
        self._input_rules: List[UserInputRuleSet] = []
        self._move_rules: List[TileMovementRule] = []
        self._player_id = player_id

    def get_player_id(self):
       return self._player_id

    def get_live_tiles(self) -> Optional[BoardElementSet]:
        return self._live_tiles

    def set_live_tile(self, live_tiles: BoardElementSet):
        self._live_tiles = live_tiles

    def has_live_tiles(self) -> bool:
        return self._live_tiles is not None

    def set_tile_match_rule(self, match_rule: TileMatchRule):
        self._match_rule = match_rule

    def set_tile_generator_rule(self, generator_rule: TileGeneratorRule):
        self._generator_rule = generator_rule

    def add_user_input_rule(self, input_rule: UserInputRule, input_set: Set[DirectionButton | ActionButton]):
        self._input_rules.append(UserInputRuleSet(input_rule, input_set))

    def add_move_rule(self, move_rule: TileMovementRule):
        self._move_rules.append(move_rule)

    def get_user_input_rules(self) -> Iterable[UserInputRuleSet]:
        return self._input_rules

    def get_height(self) -> int:
        return self._tiles.rows

    def get_width(self) -> int:
        return self._tiles.cols

    def get_tile_at(self, coordinate: Coordinate) -> TileElement:
        return self._tiles.get_mutable(coordinate.y, coordinate.x)

    def is_valid_coordinate(self, coordinate: Coordinate):
        return (coordinate.x in range(self._tiles.cols) and
                coordinate.y in range(self._tiles.rows))


    def swap_tile_contents(self, c1: Coordinate, c2: Coordinate):
        """
        Swaps the contents of two tiles at specified coordinate. Note that
        this does not whether tiles elements have support_tile_move set to False
        :param c1: coordinate 1
        :param c2: coordinate 2
        """
        self._tiles.swap(c1.y, c1.x, c2.y, c2.x)


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
        for move_rule in self._move_rules:
            move_rule.move_tiles(self)

    def spawn_tiles(self):
        if self._generator_rule:
            generated_tiles = self._generator_rule.produce_tiles(self)
            if generated_tiles:
                print(f"Generated {len(generated_tiles.get_element_pairs())} tiles")
