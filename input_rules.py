from turtledemo.sorting_animate import enable_keys
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


class HorizontalShiftLiveTileRule(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if not board.has_live_tiles():
            return

        # Get the direction to move
        direction = None
        if event == DirectionButton.LEFT:
            print("Moving Tetris block left")
            direction = Coordinate(-1, 0)
        elif event == DirectionButton.RIGHT:
            print("Moving Tetris block right")
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
            print("Moving Tetris block down")
            self._move_live_tiles_down(board)
        elif event == DirectionButton.UP:
            print("Up movement not allowed in Tetris")

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
#
#     def _lock_live_tiles(self, board: Board):
#         """Convert live tiles to static tiles when they can't move down anymore."""
#         if board.has_live_tiles():
#             live_tiles = board.get_live_tiles()
#
#             # Add each live tile to the static board
#             for pair in live_tiles.get_element_pairs():
#                 board.get_tile_at(pair.coordinate).add_game_element(pair.element)
#
#             # Clear the live tiles
#             board.set_live_tile(BoardElementSet())
#
#             # Generate new tetris piece
#             new_piece = generate_centered_piece(board)
#             if new_piece:
#                 board.set_live_tile(new_piece)
#
#
# def generate_centered_piece(board: Board):
#     """
#     Generate a new Tetris piece and center it at the top of the board.
#     Returns the centered piece as a BoardElementSet or None if generation failed.
#     """
#     try:
#         # Try to get a piece from the generator rule
#         generated_elements = board._generator_rule.produce_tiles(board)
#         if generated_elements is not None and len(generated_elements.get_element_pairs()) > 0:
#             # Place the piece at the top center of the board
#             centered_piece = BoardElementSet()
#             center_x = board.get_width() // 2 - 1
#
#             # Check for collisions with existing blocks
#             collision = False
#             for pair in generated_elements.get_element_pairs():
#                 new_x = center_x + pair.coordinate.x
#                 new_y = pair.coordinate.y
#
#                 # Check if position is valid
#                 if (new_x < 0 or new_x >= board.get_width() or
#                     new_y < 0 or new_y >= board.get_height()):
#                     collision = True
#                     break
#
#                 # Check if position is already occupied
#                 tile = board.get_tile_at(Coordinate(new_x, new_y))
#                 if tile and tile.has_elements():
#                     collision = True
#                     break
#
#             # If no collision, create the centered piece
#             if not collision:
#                 for pair in generated_elements.get_element_pairs():
#                     new_x = center_x + pair.coordinate.x
#                     new_y = pair.coordinate.y
#                     centered_piece.add_element(pair.element, Coordinate(new_x, new_y))
#
#                 print("New piece generated")
#                 return centered_piece
#             else:
#                 print("Collision detected when placing new piece - game might be over")
#                 return None
#         else:
#             print("Generator didn't produce pieces, creating fallback piece")
#             # Create a fallback piece using one of our predefined pieces
#             import random
#             pieces = create_tetris_pieces()
#             fallback_piece = random.choice(pieces)
#
#             # Center the fallback piece at the top of the board
#             centered_piece = BoardElementSet()
#             center_x = board.get_width() // 2 - 1
#
#             # Check for collisions with existing blocks
#             collision = False
#             for pair in fallback_piece.get_element_pairs():
#                 new_x = center_x + pair.coordinate.x
#                 new_y = pair.coordinate.y
#
#                 # Check if position is valid
#                 if (new_x < 0 or new_x >= board.get_width() or
#                     new_y < 0 or new_y >= board.get_height()):
#                     collision = True
#                     break
#
#                 # Check if position is already occupied
#                 tile = board.get_tile_at(Coordinate(new_x, new_y))
#                 if tile and tile.has_elements():
#                     collision = True
#                     break
#
#             # If no collision, create the centered piece
#             if not collision:
#                 for pair in fallback_piece.get_element_pairs():
#                     new_x = center_x + pair.coordinate.x
#                     new_y = pair.coordinate.y
#                     centered_piece.add_element(pair.element, Coordinate(new_x, new_y))
#
#                 return centered_piece
#             else:
#                 print("Collision detected when placing fallback piece - game over")
#                 return None
#     except Exception as e:
#         print(f"Error generating new piece: {e}")
#         return None
