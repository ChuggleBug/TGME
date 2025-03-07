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

    # TODO: implement other shifters
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
        ...

    def _shift_all_down(self, board: Board):
        for row in reversed(range(board.get_num_rows())):
            for col in range(board.get_num_columns()):
                for i in range(self._shift_amount):
                    src_coordinate = Coordinate(col, row + i)
                    target_coordinate = Coordinate(col, row + 1 + i)
                    if (not board.is_valid_coordinate(target_coordinate) or
                            board.get_tile_at(row+1 + i, col).has_elements() or
                            not board.get_tile_at(row, col).can_support_move()):
                        continue
                    board.swap_tile_contents(src_coordinate, target_coordinate)

    def _shift_all_left(self, board: Board):
        ...

    def _shift_all_right(self, board: Board):
        ...


class ShiftLiveTiles(TileMovementRule):

    def __init__(self):
        # by convenience
        self._shift_direction: int = 1
        self._shift_direction: ShiftDirection = ShiftDirection.DOWN

    def move_tiles(self, board: Board):
        pass