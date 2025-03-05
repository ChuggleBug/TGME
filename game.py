

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

    def bind(self, controller: ButtonController, board: Board):
        self._board = board
        self._controller = controller
        for ruleset in board.get_user_input_rules():
            # Defined here for debugging purposes
            event_handler = lambda event: ruleset.input_rule.handle_input(board, event=event)
            for button in ruleset.input_set:
                # If you want to know why this looks weird, look up "lambda late binding"
                controller.on_button(button=button,
                                     fn=lambda event, rs=ruleset: rs.input_rule.handle_input(board, event=event))

    def get_window(self):
        return self._window

    def start(self):
        self._controller.start_controller()
        self._window.mainloop()