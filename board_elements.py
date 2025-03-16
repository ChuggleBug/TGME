from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from constants import Color

if TYPE_CHECKING:
    from board import Board

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
    supports_tile_move: bool = field(default=True)
    # Live tiles can move through this element
    supports_move_through: bool = field(default=True)
    # The element "absorbs" a destroy
    do_block_destroy: bool = field(default=False)

    @abstractmethod
    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        """
        Draw this game element on the provided canvas within the bounding box.
        
        Args:
            canvas: The tkinter canvas to draw on
            x1, y1: Top-left corner coordinates
            x2, y2: Bottom-right corner coordinates
        """
        pass


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

    @classmethod
    def shift_elements(cls, e_set: ElementSet, *, horizontal: int = 0, vertical: int = 0) -> ElementSet:
        shifted_set = e_set.__class__()
        for pair in e_set.get_element_pairs():
            shift_coordinate = copy.deepcopy(pair.coordinate)
            shift_coordinate.x += horizontal
            shift_coordinate.y += vertical
            shifted_set.add_element(pair.element, shift_coordinate)
        return shifted_set

    def __repr__(self):
        return f'{self.__class__.__name__}(size={len(self._elements)}, elements={self._elements}'


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
            # if converted_coords.x > board.get_width() or converted_coords.y > board.get_height():
            #     raise ValueError(f"{converted_coords} have elements outside of the bounds of the board [(0-0),({board.get_width()},{board.get_height()})]")
            converted_set.add_element(pair.element, converted_coords)

        return converted_set

    def get_width(self) -> int:
        left_x = min(map(lambda t: t.coordinate.x, self._elements))
        right_x = max(map(lambda t: t.coordinate.x, self._elements))
        return right_x - left_x + 1

    def get_height(self) -> int:
        top_y = min(map(lambda t: t.coordinate.y, self._elements))
        bottom_y = max(map(lambda t: t.coordinate.y, self._elements))
        return bottom_y - top_y + 1

    def rotate_counterclockwise(self) -> None:
        """
        Rotate the tile set 90 degrees counterclockwise relative to its center
        """
        if not self._elements:
            return

        # plain 90 degree rotation
        for pair in self.get_element_pairs():
            pair.coordinate.x, pair.coordinate.y = -1 * pair.coordinate.y, pair.coordinate.x

        # reorganize the origin to the new top right
        top_right = Coordinate(
            x=min(map(lambda pair: pair.coordinate.x, self.get_element_pairs())),
            y=min(map(lambda pair: pair.coordinate.y, self.get_element_pairs())),
        )
        for pair in self.get_element_pairs():
            pair.coordinate = pair.coordinate - top_right

    def rotate_clockwise(self) -> None:
        """
        Rotate the tile set 90 degrees clockwise relative to its center
        """
        if not self._elements:
            return

        # plain 90 degree rotation
        for pair in self.get_element_pairs():
            pair.coordinate.x, pair.coordinate.y = pair.coordinate.y, -1 * pair.coordinate.x

        # reorganize the origin to the new top right
        top_right = Coordinate(
            x=min(map(lambda pair: pair.coordinate.x, self.get_element_pairs())),
            y=min(map(lambda pair: pair.coordinate.y, self.get_element_pairs())),
        )
        for pair in self.get_element_pairs():
            pair.coordinate = pair.coordinate - top_right


class BoardElementSet(ElementSet):
    def as_relative_coordinates(self) -> RelativeElementSet:
        element_set = RelativeElementSet()
        origin = self.get_top_right()
        for pair in self.get_element_pairs():
            element_set.add_element(
                element=pair.element,
                coordinate=pair.coordinate - origin
            )
        return element_set

    def get_top_right(self) -> Coordinate:
        # top right = lowest x, lowest y
        return Coordinate(
            x=min(map(lambda pair: pair.coordinate.x, self.get_element_pairs())),
            y=min(map(lambda pair: pair.coordinate.y, self.get_element_pairs())),
        )


@dataclass
class Coordinate:
    x: int
    y: int

    def __add__(self, other: Any) -> Coordinate:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Any) -> Coordinate:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return Coordinate(self.x - other.x, self.y - other.y)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Coordinate):
            return False
        return self.x == other.x and self.y == other.y
