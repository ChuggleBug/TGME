from __future__ import annotations
from  typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from constants import Color

if TYPE_CHECKING:
    from board import Coordinate, Board

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
            if converted_coords.x > board.get_width() or converted_coords.y > board.get_height():
                raise ValueError(f"{converted_coords} have elements outside of the bounds of the board [(0-0),({board.get_width()},{board.get_height()})]")
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


class BoardElementSet(ElementSet):
    def as_relative_coordinates(self) -> RelativeElementSet:
        ...
