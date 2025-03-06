
from rules import *
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from gameboard import Board


class LeftRightInput(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if event == DirectionButton.LEFT:
            print("Left Input")
        elif event == DirectionButton.RIGHT:
            print("Right Input")

class UpDownInput(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if event == DirectionButton.UP:
            print("Up Input")
        elif event == DirectionButton.DOWN:
            print("Down Input")

class ActionInput(UserInputRule):
    def handle_input(self, board, *, event):
        if event == ActionButton.PRIMARY:
            print("Primary Action")
        elif event == ActionButton.SECONDARY:
            print("Secondary Action")
        print("Test: Will check matches")
        board._match_rule.check_matches(board)

class TestTileMatch(TileMatchRule):
    def check_matches(self, board):
        print("I am checking matches")

if __name__ == '__main__':
    # Constructors
    game = Game()
    board = Board(rows=5, cols=5)
    controller = KeyboardController()

    # Set rules dictating what happens for user input
    board.set_tile_match_rule(TestTileMatch())
    board.set_tile_generator_rule(FillEmptySpots())
    board.add_user_input_rule(UpDownInput(), {DirectionButton.UP, DirectionButton.DOWN})
    board.add_user_input_rule(LeftRightInput(), {DirectionButton.LEFT, DirectionButton.RIGHT}) # board will perform rule for these set of inputs
    board.add_user_input_rule(ActionInput(), {ActionButton.PRIMARY, ActionButton.SECONDARY})

    # Associated input rules for the board will now be executed from the associated controller
    game.bind(controller, board)

    # tkinter specific
    controller.bind_to_window(game.get_window())

    # start game
    game.start()
