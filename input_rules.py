from typing import Union

from board import Board
from board_elements import RelativeElementSet, BoardElementSet, Coordinate
from button_controller import DirectionButton, ActionButton
from rules import UserInputRule


class DoNothingRule(UserInputRule):
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        pass


class RotateLiveTilesRule(UserInputRule):
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
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


class HorizontalShiftLiveTileRule(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if not board.has_live_tiles():
            return

        # Get the direction to move
        direction = None
        if event == DirectionButton.LEFT:
            direction = Coordinate(-1, 0)
        elif event == DirectionButton.RIGHT:
            direction = Coordinate(1, 0)

        if direction:
            # Try to move the live tiles in the specified direction
            self._move_live_tiles(board, direction)

    def _move_live_tiles(self, board: Board, direction: Coordinate):
        """Move the live tiles if the move is valid."""
        live_tiles = board.get_live_tiles()
        # Create a new set with the moved positions
        new_positions = BoardElementSet()

        # Check if the move is valid (no collisions)
        can_move = True
        for pair in live_tiles.get_element_pairs():
            new_pos = pair.coordinate + direction

            # Check boundaries
            if (new_pos.x < 0 or new_pos.x >= board.get_width() or
                new_pos.y < 0 or new_pos.y >= board.get_height()):
                can_move = False
                break

            # Check collision with static elements
            tile = board.get_tile_at(new_pos)
            if tile and tile.has_elements():
                # If there's any element in this tile, we can't move there
                can_move = False
                break

        # If move is valid, update live tiles positions
        if can_move:
            for pair in live_tiles.get_element_pairs():
                new_pos = pair.coordinate + direction
                new_positions.add_element(pair.element, new_pos)

            # Update the board's live tiles
            board.set_live_tile(new_positions)


class DownwardsShiftLiveTileRule(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if not board.has_live_tiles():
            return

        # Tetris pieces should only move down, not up
        if event == DirectionButton.DOWN:
            self._move_live_tiles_down(board)
        elif event == DirectionButton.UP:
            pass

    def _move_live_tiles_down(self, board: Board):
        """Move the live tiles down if possible."""
        direction = Coordinate(0, 1)  # Down
        live_tiles = board.get_live_tiles()
        new_positions = BoardElementSet()

        # Check if downward movement is valid
        can_move = True
        for pair in live_tiles.get_element_pairs():
            new_pos = pair.coordinate + direction

            # Check if new position is out of bounds
            if new_pos.y >= board.get_height():
                can_move = False
                break

            # Check collision with static elements
            tile = board.get_tile_at(new_pos)
            if tile and tile.has_elements():
                # If there's any element in this tile, we can't move there
                can_move = False
                break

        # If can move down, update positions
        if can_move:
            for pair in live_tiles.get_element_pairs():
                new_pos = pair.coordinate + direction
                new_positions.add_element(pair.element, new_pos)

            # Update the board's live tiles
            board.set_live_tile(new_positions)
        else:
            # If can't move down, convert live tiles to static tiles
            board.lock_live_tiles_to_board()


class CursorApplyDirectionRule(UserInputRule):
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        cursor = board.get_cursor()
        primary_coordinate = cursor.get_primary_position()
        test_coordinate = primary_coordinate # stub initialization
        if event == DirectionButton.UP:
            test_coordinate = primary_coordinate + Coordinate(0, -1)
        elif event == DirectionButton.DOWN:
            test_coordinate = primary_coordinate + Coordinate(0, 1)
        elif event == DirectionButton.LEFT:
            test_coordinate = primary_coordinate + Coordinate(-1, 0)
        elif event == DirectionButton.RIGHT:
            test_coordinate = primary_coordinate + Coordinate(1, 0)

        if not board.is_valid_coordinate(test_coordinate):
            return
        if cursor.is_in_movement_state():
            cursor.set_primary_position(test_coordinate)
        else:  # in secondary state
            cursor.set_secondary_position(test_coordinate)

class CursorApplySelectionRule(UserInputRule):
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        cursor = board.get_cursor()
        if event == ActionButton.PRIMARY:
            if cursor.is_in_swapping_state() and cursor.has_secondary_position():
                if (board.get_tile_at(cursor.get_primary_position()).can_support_move() and
                        board.get_tile_at(cursor.get_secondary_position()).can_support_move()):
                    board.swap_tile_contents(cursor.get_primary_position(), cursor.get_secondary_position())
                    # A match was not made, revert
                    if not len(board.get_tile_match_rule().check_matches(board)) > 0:
                        board.swap_tile_contents(cursor.get_primary_position(), cursor.get_secondary_position())
                    else:
                        cursor.set_movement_state()
            else:
                cursor.set_swapping_state()
        elif event == ActionButton.SECONDARY:
            cursor.set_movement_state()