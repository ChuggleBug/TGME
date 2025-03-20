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
    from typing import List
    from board import Board

_GAME_OVER_TEXT = 'Game Over!'

@dataclass
class BoardWindow:
    board: Board
    canvas: tk.Canvas

class Game:
    TOTAL_BOARD_WIDTH = 500
    TOTAL_BOARD_HEIGHT = 500

    def __init__(self):
        self._window = tk.Tk()
        self._window.attributes('-topmost', True)

        self._window.title("Tile Matching Game")
        self.update_interval = 100  # 100ms (10 updates per second)
        self._boards: List[BoardWindow] = []
        self._controllers: List[ButtonController] = []

        self.scores = {}
        self.score_labels = {}

    def update_score(self, board: Board, points: int):
        if board not in self.scores:
            self.scores[board] = 0  
        self.scores[board] += points
        self.score_labels[board].config(text=f"Score: {self.scores[board]}")


    def bind(self, controller: ButtonController, *, board_index: int):
        board = self.get_board(board_index)
        self._controllers.append(controller)
        for ruleset in board.get_user_input_rules():
            for button in ruleset.input_set:
                # If you want to know why this looks weird, look up "lambda late binding"
                controller.on_button(button=button,
                                     fn=lambda event, rs=ruleset: rs.input_rule.handle_input(board, event=event))

    def add_board(self, board: Board):
        frame = tk.Frame(self._window, bg="black")
        frame.grid(row=0, column=len(self._boards), padx=20, pady=10)  

        score_label = tk.Label(frame, text=f"Score: 0", font=("Arial", 16, "bold"), bg="black", fg="white")
        score_label.pack(pady=5) 

        canvas = tk.Canvas(frame, width=Game.TOTAL_BOARD_WIDTH, height=Game.TOTAL_BOARD_HEIGHT, bg=TK_COLOR_MAP[Color.BLACK])
        board.set_game(self)  
        board_window = BoardWindow(board=board, canvas=canvas)

        self._boards.append(board_window)
        
        canvas.pack()

        self.score_labels[board] = score_label
        self.scores[board] = 0

        self._window.update()

        
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

        # Calculate individual tile dimensions to stretch and fill the fixed board area
        board_height = board.get_height()
        board_width = board.get_width()

        # Instead of using min to get square cells, calculate separate dimensions
        # This will stretch tiles to fill the entire board area
        cell_width = Game.TOTAL_BOARD_WIDTH / board_width
        cell_height = Game.TOTAL_BOARD_HEIGHT / board_height

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

                canvas.create_rectangle(x1, y1, x2, y2, outline=TK_COLOR_MAP[Color.WHITE], width=0)

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

        if board.is_game_over():
            Game._write_game_over(canvas)

    @staticmethod
    def _write_game_over(canvas: tk.Canvas):
        canvas.create_text(
            Game.TOTAL_BOARD_WIDTH // 2,
            Game.TOTAL_BOARD_HEIGHT // 2,
            text=_GAME_OVER_TEXT,
            anchor='center',
            fill=TK_COLOR_MAP[Color.RED],
            font=('Impact', min(Game.TOTAL_BOARD_WIDTH // 7, Game.TOTAL_BOARD_HEIGHT // 7))
        )

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
