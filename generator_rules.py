
from __future__ import annotations
from typing import  TYPE_CHECKING

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import random
import copy

from gameboard import Board, RelativeElementSet, BoardElementSet, Coordinate
from rules import TileGeneratorRule, ElementGenerationFailException

if TYPE_CHECKING:
    from gameboard import GameElement
    from typing import List, Tuple, Optional


T = TypeVar("T")


class ElementProvider(ABC, Generic[T]):
    @abstractmethod
    def provide(self) -> T:
        """
        Returns an instance of T.

        It is up to the implementing class as how to return a value
        :return: Any object of type T
        """
        ...


class RandomElementProvider(ElementProvider, Generic[T]):

    def __init__(self):
        self._elementChoices: List[Tuple[T, int]] = []

    def add_choice(self, *, option: T, weight: int):
        """
        Add a potential element which can be chosen from at random.
        Weight values should be a number from 0 to 100 representing the
        percen chance of it occurring
        :param option: Element which can be chosen
        :param weight: Percent chance of it occurring as an integer
        """
        if weight < 0 or weight > 100:
            raise ValueError(f"weight={weight} not in range [0-100]")
        if sum(map(lambda t: t[1], self._elementChoices), start=weight) > 100:
            raise ValueError("Percent of element chances exceeds 100")
        self._elementChoices.append((option, weight))

    def _generate_random(self) -> T:
        options, weights = zip(*self._elementChoices)  # Unpack elements and weights
        return copy.deepcopy(random.choices(options, weights=weights)[0])

    def provide(self) -> T:
        if sum(map(lambda t: t[1], self._elementChoices)) != 100:
            raise ValueError("Sum of weights is not equal to 100")
        return self._generate_random()


class FillEmptyTopRowSpotsRule(TileGeneratorRule):
    def __init__(self):
        self._provider: Optional[ElementProvider[GameElement]] = None

    def set_provider(self, provider: ElementProvider[GameElement]):
        self._provider = provider

    def produce_tiles(self, board: Board) -> Optional[BoardElementSet]:
        if self._provider is None:
            raise ValueError("Element Provider is missing")
        # Check the top row of the board has any sports which
        # can have a tiled spawn on them
        top_row_elements = BoardElementSet()

        for i in range(board.get_num_columns()):
            if board.get_tile_at(0, i).can_support_tile_spawn():
                top_row_elements.add_element(self._provider.provide(), Coordinate(x=i, y=0))

        return top_row_elements if top_row_elements.has_elements() else None

class DropElementSetRule(TileGeneratorRule):

    def __init__(self):
        self._provider: Optional[ElementProvider[RelativeElementSet]] = None

    def set_provider(self, provider: ElementProvider[RelativeElementSet]):
        self._provider = provider

    def produce_tiles(self, board: Board) -> Optional[BoardElementSet]:
        if self._provider is None:
            raise ValueError("Element Provider is missing")

        # only make an element is there is no live tile set
        if board.has_live_tiles():
            return None

        new_set: RelativeElementSet = self._provider.provide()
        insert = _get_centered_tile_set_coordinates(board, new_set)
        active_set: BoardElementSet = new_set.as_board_coordinates(board, insert)

        for element in active_set.get_elements():
            if not board.get_tile_at(element[1].x, element[1].x).can_support_tile_spawn():
                raise ElementGenerationFailException()

        board.set_live_tile(active_set)
        return None # live tiles is responsible for managing the tiles generated here

# TODO: maybe this can be configured in a method? inside of DropElementSetRule
def _get_centered_tile_set_coordinates(board: Board, tile_set: RelativeElementSet) -> Coordinate:
    return Coordinate(x=(board.get_num_columns() // 2) - (tile_set.get_width() // 2), y=0)