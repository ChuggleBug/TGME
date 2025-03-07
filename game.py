
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
        cell_size = 100
        for y in range(self._board.get_height()):
            for x in range(self._board.get_width()):
                x1 = x * cell_size
                x2 = x1 + cell_size
                y1 = y * cell_size
                y2 = y1 + cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3)

                tile_element = self._board.get_tile_at(Coordinate(x,y))
                if tile_element and tile_element._elements:
                    print(f"Tile at ({Coordinate(x,y)}): {tile_element._elements[0].element_name}")
                    tile_color = TK_COLOR_MAP.get(tile_element._elements[0].element_color, "white")
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=tile_color, outline="white", width=3)

    def get_window(self):
        return self._window

    def start(self):
        self._controller.start_controller()
        self.render_board()
        self._window.mainloop()