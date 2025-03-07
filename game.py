from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk

from button_controller import ButtonController
from board import Coordinate
from constants import TK_COLOR_MAP

if TYPE_CHECKING:
    from typing import Optional
    from board import Board


# TODO: Implement support for two players
# TODO: theoretically, this can be done by having support for two boards, controller
# TODO: pairs and then updating the tkinter window accordingly
class Game:
    def __init__(self):
        self._window = tk.Tk()
        self._board: Optional[Board] = None
        self._controller: Optional[ButtonController] = None
        self._window.title("Tile Matching Game")
        self.canvas = tk.Canvas(self._window, width=500, height=500, bg="black")
        self.canvas.pack()

    def bind(self, controller: ButtonController, board: Board):
        self._board = board
        self._controller = controller
        for ruleset in board.get_user_input_rules():
            for button in ruleset.input_set:
                # If you want to know why this looks weird, look up "lambda late binding"
                controller.on_button(button=button,
                                     fn=lambda event, rs=ruleset: rs.input_rule.handle_input(board, event=event))

    # TODO: Board might have a live tile. If it does, then it should be drawn after drawing all the static elements
    def render_board(self):
        # Set fixed board display size (in pixels)
        total_board_width = 500
        total_board_height = 500
        
        # Calculate individual tile dimensions to stretch and fill the fixed board area
        board_height = self._board.get_height()
        board_width = self._board.get_width()
        
        # Instead of using min to get square cells, calculate separate dimensions
        # This will stretch tiles to fill the entire board area
        cell_width = total_board_width // board_width
        cell_height = total_board_height // board_height
        
        # First, clear the canvas to prevent overlapping elements
        self.canvas.delete("all")
        
        # Draw the grid and static tiles
        for y in range(self._board.get_height()):
            for x in range(self._board.get_width()):
                # Calculate coordinates using separate width/height
                x1 = x * cell_width
                x2 = x1 + cell_width
                y1 = y * cell_height
                y2 = y1 + cell_height

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3)

                tile_element = self._board.get_tile_at(Coordinate(x,y))
                if tile_element and tile_element.has_elements():
                    elements = tile_element.get_elements()
                    print(f"Tile at ({Coordinate(x,y)}): {elements[0].element_name}")
                    # Use each element's draw method instead of drawing directly
                    for element in elements:
                        element.draw(self.canvas, x1, y1, x2, y2)
        
        # Draw any live tiles on top of the static board elements
        if self._board.has_live_tiles():
            live_tiles = self._board.get_live_tiles()
            for pair in live_tiles.get_element_pairs():
                coord = pair.coordinate
                # Use separate width/height for live tiles too
                x1 = coord.x * cell_width
                x2 = x1 + cell_width
                y1 = coord.y * cell_height
                y2 = y1 + cell_height
                
                # Draw the live tile (similar to static tiles)
                element = pair.element
                element.draw(self.canvas, x1, y1, x2, y2)

    def get_window(self):
        return self._window

    def start(self):
        self._controller.start_controller()
        self.render_board()
        self._window.mainloop()