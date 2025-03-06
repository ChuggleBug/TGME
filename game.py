

from button_controller import *
from gameboard import Board
from rules import *


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

        
        self.render_board()
        for ruleset in board.get_user_input_rules():
            # Defined here for debugging purposes
            event_handler = lambda event: ruleset.input_rule.handle_input(board, event=event)
            for button in ruleset.input_set:
                # If you want to know why this looks weird, look up "lambda late binding"
                controller.on_button(button=button,
                                     fn=lambda event, rs=ruleset: rs.input_rule.handle_input(board, event=event))
    
    def render_board(self):
        cell_size = 100
        for row in range(self._board.get_rows()):
            for col in range(self._board.get_cols()):
                x1 = row * cell_size
                x2 = x1 + cell_size
                y1 = col * cell_size
                y2 = y1 + cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3)



    def get_window(self):
        return self._window

    def start(self):
        self._controller.start_controller()
        self._window.mainloop()