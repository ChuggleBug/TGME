from gameboard import Board, Coordinate
from rules import TileMovementRule
from enum import Enum, auto

class ShiftDirection(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class ShiftStaticTilesRule(TileMovementRule):

    def __init__(self):
        # by convenience
        self._shift_direction: int = 1
        self._shift_direction: ShiftDirection = ShiftDirection.DOWN

    def move_tiles(self, board: Board):
        if self._shift_direction == ShiftDirection.UP:
            self._shift_all_up(board)
        elif self._shift_direction == ShiftDirection.DOWN:
            self._shift_all_down(board)
        elif self._shift_direction == ShiftDirection.LEFT:
            self._shift_all_left(board)
        elif self._shift_direction == ShiftDirection.RIGHT:
            self._shift_all_right(board)

    def _shift_all_up(self, board: Board):
        for y in range(board.get_height()):
            for x in range(board.get_width()):
                for i in range(self._shift_amount):
                    source_coordinate = Coordinate(x, y - i)
                    target_coordinate = Coordinate(x, y - i - 1)
                    if (not board.is_valid_coordinate(target_coordinate) or
                            board.get_tile_at(target_coordinate).has_elements() or
                            not board.get_tile_at(source_coordinate).can_support_move()):
                        continue
                    board.swap_tile_contents(source_coordinate, target_coordinate)

    # This one was the original source
    def _shift_all_down(self, board: Board):
        for y in reversed(range(board.get_height())):
            for x in range(board.get_width()):
                for i in range(self._shift_amount):
                    source_coordinate = Coordinate(x, y + i)
                    target_coordinate = Coordinate(x, y + i + 1)
                    if (not board.is_valid_coordinate(target_coordinate) or
                            board.get_tile_at(target_coordinate).has_elements() or
                            not board.get_tile_at(source_coordinate).can_support_move()):
                        continue
                    board.swap_tile_contents(source_coordinate, target_coordinate)

    def _shift_all_left(self, board: Board):
        for x in range(board.get_width()):  # Iterate left to right
            for y in range(board.get_height()):
                for i in range(self._shift_amount):
                    source_coordinate = Coordinate(x - i, y)  # Move left
                    target_coordinate = Coordinate(x - i - 1, y)
                    if (not board.is_valid_coordinate(target_coordinate) or
                            board.get_tile_at(target_coordinate).has_elements() or
                            not board.get_tile_at(source_coordinate).can_support_move()):
                        continue
                    board.swap_tile_contents(source_coordinate, target_coordinate)

    def _shift_all_right(self, board: Board):
        for x in reversed(range(board.get_width())):  # Iterate right to left
            for y in range(board.get_height()):
                for i in range(self._shift_amount):
                    source_coordinate = Coordinate(x + i, y)  # Move right
                    target_coordinate = Coordinate(x + i + 1, y)
                    if (not board.is_valid_coordinate(target_coordinate) or
                            board.get_tile_at(target_coordinate).has_elements() or
                            not board.get_tile_at(source_coordinate).can_support_move()):
                        continue
                    board.swap_tile_contents(source_coordinate, target_coordinate)


class ShiftLiveTiles(TileMovementRule):

    def __init__(self):
        # by convenience
        self._shift_direction: int = 1
        self._shift_direction: ShiftDirection = ShiftDirection.DOWN

    def move_tiles(self, board: Board):
        pass