from __future__ import annotations


from board import Board
from board_elements import Coordinate, BoardElementSet
from rules import GravityRule


# This class handles the automatic downward movement (gravity) for falling pieces
class DownwardGravityRule(GravityRule):
    def __init__(self, drop_interval=1000):  # Default: 1 second (1000ms)
        self.drop_interval = drop_interval
        self.last_drop_time = 0

    def update(self, board: Board, current_time):
        """Check if it's time to drop the piece based on the timer."""
        if not board.has_live_tiles():
            return

        # If enough time has passed, drop the piece
        if current_time - self.last_drop_time >= self.drop_interval:
            self._drop_piece(board)
            self.last_drop_time = current_time

    def _drop_piece(self, board: Board):
        """Move the piece down one cell."""
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
            # self._lock_live_tiles(board)

    def _lock_live_tiles(self, board: Board):
        """Convert live tiles to static tiles when they can't move down anymore."""
        if board.has_live_tiles():
            live_tiles = board.get_live_tiles()

            # Add each live tile to the static board
            for pair in live_tiles.get_element_pairs():
                board.get_tile_at(pair.coordinate).add_game_element(pair.element)

            # Clear the live tiles
            board.set_live_tile(BoardElementSet())

            # Generate new tetris piece - using a function from main.py
            # The function itself remains in main.py, we just call it from here
            from input_rules import generate_centered_piece
            new_piece = generate_centered_piece(board)
            if new_piece:
                board.set_live_tile(new_piece)
