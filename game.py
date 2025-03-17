from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass
import tkinter as tk
import time

from button_controller import ButtonController
from board_elements import Coordinate
from constants import TK_COLOR_MAP
from constants import Color

if TYPE_CHECKING:
    from typing import Optional, List
    from board import Board

@dataclass
class BoardWindow:
    board: Board
    canvas: tk.Canvas

# TODO: Implement support for two players
# TODO: theoretically, this can be done by having support for two boards, controller
# TODO: pairs and then updating the tkinter window accordingly
class Game:
    def __init__(self):
        self._window = tk.Tk()
        # self._board: Optional[Board] = None
        # self._controller: Optional[ButtonController] = None
        self._window.title("Tile Matching Game")
        # self.canvas = tk.Canvas(self._window, width=500, height=500, bg=TK_COLOR_MAP[Color.BLACK])
        # self.canvas.pack()
        # For automatic block dropping
        self.update_interval = 100  # 100ms (10 updates per second)
        self._boards: List[BoardWindow] = []
        self._controllers: List[ButtonController] = []

    def bind(self, controller: ButtonController, *, board_index: int):
        board = self.get_board(board_index)
        self._controllers.append(controller)
        for ruleset in board.get_user_input_rules():
            for button in ruleset.input_set:
                # If you want to know why this looks weird, look up "lambda late binding"
                controller.on_button(button=button,
                                     fn=lambda event, rs=ruleset: rs.input_rule.handle_input(board, event=event))

    def add_board(self, board: Board):
        canvas = tk.Canvas(self._window, width=500, height=500, bg=TK_COLOR_MAP[Color.BLACK])
        self._boards.append(BoardWindow(board, canvas))
        canvas.pack()

    def get_board(self, index: int, /) -> Board:
        if index not in range(len(self._boards)):
            raise IndexError
        return self._boards[index].board

    def get_window(self):
        return self._window

    def _render_boards(self):
        for board_window in self._boards:
            self._render_board(board_window)

    @staticmethod
    def _render_board(board_window: BoardWindow):
        board = board_window.board
        canvas = board_window.canvas

        # Set fixed board display size (in pixels)
        total_board_width = 500
        total_board_height = 500

        # Calculate individual tile dimensions to stretch and fill the fixed board area
        board_height = board.get_height()
        board_width = board.get_width()

        # Instead of using min to get square cells, calculate separate dimensions
        # This will stretch tiles to fill the entire board area
        cell_width = total_board_width // board_width
        cell_height = total_board_height // board_height

        # First, clear the canvas to prevent overlapping elements
        canvas.delete("all")

        # Draw the grid and static tiles
        for y in range(board.get_height()):
            for x in range(board.get_width()):
                # Calculate coordinates using separate width/height
                x1 = x * cell_width
                x2 = x1 + cell_width
                y1 = y * cell_height
                y2 = y1 + cell_height

                canvas.create_rectangle(x1, y1, x2, y2, outline=TK_COLOR_MAP[Color.WHITE], width=3)

                tile_element = board.get_tile_at(Coordinate(x,y))
                if tile_element and tile_element.has_elements():
                    elements = tile_element.get_elements()
                    # Use each element's draw method instead of drawing directly
                    for element in elements:
                        element.draw(canvas, x1, y1, x2, y2)

        # Draw any live tiles on top of the static board elements
        if board.has_live_tiles():
            live_tiles = board.get_live_tiles()
            for pair in live_tiles.get_element_pairs():
                coord = pair.coordinate
                # Use separate width/height for live tiles too
                x1 = coord.x * cell_width
                x2 = x1 + cell_width
                y1 = coord.y * cell_height
                y2 = y1 + cell_height

                # Draw the live tile (similar to static tiles)
                element = pair.element
                element.draw(canvas, x1, y1, x2, y2)

        # Draw cursor on board if supported by game
        if board.has_cursor():
            board.get_cursor().draw(canvas, cell_height, cell_width)

    def update(self):
        """Update game state and redraw."""
        # Apply gravity if needed
        current_time = int(time.time() * 1000)  # Get current time in milliseconds

        for board_window in self._boards:
            board_window.board.update(current_time)

        # Redraw the board
        self._render_boards()
        
        # Schedule the next update
        self._window.after(self.update_interval, self.update)

    def start(self):
        for controller in self._controllers:
            controller.start_controller()
        
        # Start the update loop
        self.update()
        
        # Start the main event loop
        self._window.mainloop()
