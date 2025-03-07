
from __future__ import annotations
from typing import TYPE_CHECKING

from gameboard import Board, RelativeElementSet, BoardElementSet, Coordinate
from provider import ElementProvider
from rules import TileGeneratorRule, ElementGenerationFailException

if TYPE_CHECKING:
    from gameboard import GameElement
    from typing import Optional


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

        for x in range(board.get_width()):
            if board.get_tile_at(Coordinate(x, 0)).can_support_tile_spawn():
                top_row_elements.add_element(self._provider.provide(), Coordinate(x=x, y=0))

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
        insert = _get_top_center_tile_set_coordinates(board, new_set)
        active_set: BoardElementSet = new_set.as_board_coordinates(board, insert)

        for pair in active_set.get_element_pairs():
            if not board.get_tile_at(pair.coordinate).can_support_tile_spawn():
                raise ElementGenerationFailException()

        board.set_live_tile(active_set)
        return None # live tiles is responsible for managing the tiles generated here

# TODO: maybe this can be configured in a method? inside of DropElementSetRule
def _get_top_center_tile_set_coordinates(board: Board, tile_set: RelativeElementSet) -> Coordinate:
    return Coordinate(x=(board.get_width() // 2) - (tile_set.get_width() // 2), y=0)


class FillAllSpotsRule(TileGeneratorRule):
    def __init__(self):
        self._provider: Optional[ElementProvider[GameElement]] = None

    def set_provider(self, provider: ElementProvider[GameElement]):
        self._provider = provider

    def produce_tiles(self, board: Board) -> Optional[GameElement]:
        generated_tiles = BoardElementSet()
        for y in range(board.get_height()):
            for x in range(board.get_width()):
                target_coordinate = Coordinate(x, y)
                if board.get_tile_at(target_coordinate).can_support_tile_spawn():
                    new_tile = self._provider.provide()
                    generated_tiles.add_element(new_tile, target_coordinate)
                #print(f"{tile._elements[0].type} ({row}, {col})")
        return generated_tiles if generated_tiles.has_elements() else None
