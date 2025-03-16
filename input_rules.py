from turtledemo.sorting_animate import enable_keys
from typing import Union

from board import Board
from board_elements import RelativeElementSet, BoardElementSet
from button_controller import DirectionButton, ActionButton
from rules import UserInputRule

class RotateLiveTiles(UserInputRule):
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        print("Trying to rotate")
        if not board.has_live_tiles():
            return
        if event not in {ActionButton.PRIMARY, ActionButton.SECONDARY}:
            return

        tile_set: BoardElementSet = board.get_live_tiles()
        rotated_set: RelativeElementSet = tile_set.as_relative_coordinates()
        if event is ActionButton.PRIMARY:
            rotated_set.rotate_clockwise()
        elif event is ActionButton.SECONDARY:
            rotated_set.rotate_counterclockwise()

        rotated_test_set: BoardElementSet = rotated_set.as_board_coordinates(board, tile_set.get_top_right())
        for pair in rotated_test_set.get_element_pairs():
            if (not board.is_valid_coordinate(pair.coordinate) or
                    not board.get_tile_at(pair.coordinate).can_move_through()):
                return

        board.set_live_tile(rotated_test_set)
