
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum, auto

from board_elements import ElementSet, Coordinate
from rules import TileMovementRule

if TYPE_CHECKING:
    from board import Board


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
        if not self._do_apply_move:
            return
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


class ShiftLiveTilesRule(TileMovementRule):

    def __init__(self):
        # by convenience
        self._shift_direction: int = 1
        self._shift_direction: ShiftDirection = ShiftDirection.DOWN

    def move_tiles(self, board: Board):
        if not self._do_apply_move:
            return
        if not board.has_live_tiles():
            return
        
        if self._shift_direction == ShiftDirection.UP:
            self._shift_all_up(board)
        elif self._shift_direction == ShiftDirection.DOWN:
            self._shift_all_down(board)
        elif self._shift_direction == ShiftDirection.LEFT:
            self._shift_all_left(board)
        elif self._shift_direction == ShiftDirection.RIGHT:
            self._shift_all_right(board)

    def _shift_all_up(self, board):
        shifted_set = board.get_live_tiles()
        for i in range(self._shift_amount):
            test_set = ElementSet.shift_elements(shifted_set, vertical=-1)
            for pair in test_set.get_element_pairs():
                if not (board.is_valid_coordinate(pair.coordinate) and
                        board.get_tile_at(pair.coordinate).can_move_through()):
                    if board.get_static_tile_move_direction() == self._shift_direction:
                        board.lock_live_tiles_to_board()
                    return
            shifted_set = test_set
        board.set_live_tile(shifted_set)

    def _shift_all_down(self, board):
        shifted_set = board.get_live_tiles()
        for i in range(self._shift_amount):
            test_set = ElementSet.shift_elements(shifted_set, vertical=1)
            for pair in test_set.get_element_pairs():
                if not (board.is_valid_coordinate(pair.coordinate) and
                        board.get_tile_at(pair.coordinate).can_move_through()):
                    if board.get_static_tile_move_direction() == self._shift_direction:
                        board.lock_live_tiles_to_board()
                    return
            shifted_set = test_set
        board.set_live_tile(shifted_set)

    def _shift_all_left(self, board: Board):
        # given the live tile set
        shifted_set = board.get_live_tiles()
        # shift all tiles in some direction (one at a time)
        for i in range(self._shift_amount):
            test_set = ElementSet.shift_elements(shifted_set, horizontal=-1)
            # check if the move was valid
            for pair in test_set.get_element_pairs():
                # If not, if it happens to be in the
                # direction that static tiles move
                if not (board.is_valid_coordinate(pair.coordinate) and
                        board.get_tile_at(pair.coordinate).can_move_through()):
                    if board.get_static_tile_move_direction() == self._shift_direction:
                        board.lock_live_tiles_to_board()
                    return
            # otherwise, continue shifting
            shifted_set = test_set
        # when the full shift was complete, set the live tile
        # set to the one that was shifted
        board.set_live_tile(shifted_set)

    def _shift_all_right(self, board):
        shifted_set = board.get_live_tiles()
        for i in range(self._shift_amount):
            test_set = ElementSet.shift_elements(shifted_set, horizontal=1)
            for pair in test_set.get_element_pairs():
                if not (board.is_valid_coordinate(pair.coordinate) and
                        board.get_tile_at(pair.coordinate).can_move_through()):
                    if board.get_static_tile_move_direction() == self._shift_direction:
                        board.lock_live_tiles_to_board()
                    return
            shifted_set = test_set
        board.set_live_tile(shifted_set)
        