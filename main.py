
from typing import TYPE_CHECKING

from generator_rules import FillAllSpotsRule, FillEmptyTopRowSpotsRule, DropElementSetRule
from rules import UserInputRule, TileMatchRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board, Coordinate
from board_elements import RelativeElementSet, BoardElementSet, GameElement
from provider import WeightedRandomElementProvider, UniformRandomElementProvider
from constants import Color

if TYPE_CHECKING:
    pass

class Candy(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

class Blocker(GameElement):
    def __init__(self):
        self.element_name = 'CandyBlocker'
        self.supports_color = False
        self.supports_tile_spawn = False


class TetrisTile(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

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


def set_candy_crush_generation(board: Board):
    # Set rules dictating how tiles are meant to be filled up
    # You can test out of rules work by changing
    # FillEmptyTopRowSpotsRule to FillAllSpotsRule
    generate_rule = FillEmptyTopRowSpotsRule()
    # Generators rules need element providers
    provider: WeightedRandomElementProvider[GameElement] = WeightedRandomElementProvider()
    provider.add_choice(option=Candy(name='CandyRed', color=Color.RED), weight=25)
    provider.add_choice(option=Candy(name='CandyBlue', color=Color.BLUE), weight=50)
    provider.add_choice(option=Candy(name='CandyGreen', color=Color.GREEN), weight=25)

    # for this example only, a blocker was added
    # a blocker prevents the spawning of candies when something tries
    # to spawn on it
    board.get_tile_at(Coordinate(0, 0)).add_game_element(Blocker())

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)


def set_tetris_generation(board: Board):
    generate_rule = DropElementSetRule()
    provider: UniformRandomElementProvider[RelativeElementSet] = UniformRandomElementProvider()

    purple_tile = TetrisTile(name="PurpleTetrisTile", color=Color.PURPLE)
    t_block = RelativeElementSet()
    t_block.add_element(element=purple_tile, coordinate=Coordinate(1,0))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(0, 1))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(1, 1))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(2, 1))

    provider.add_choice(t_block)

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)


if __name__ == "__main__":
    # Constructors
    game = Game()
    board = Board(height=5, width=5, player_id=5)
    controller = KeyboardController()

    # Set rules dictating what happens for user input
    board.set_tile_match_rule(TestTileMatch())
    board.add_user_input_rule(UpDownInput(), input_set={DirectionButton.UP, DirectionButton.DOWN})
    board.add_user_input_rule(LeftRightInput(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT}) # board will perform rule for these set of inputs
    board.add_user_input_rule(ActionInput(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})

    # Associated input rules for the board will now be executed from the associated controller
    game.bind(controller, board)

    # tkinter specific
    controller.bind_to_window(game.get_window())

    set_candy_crush_generation(board)

    # This is not good practice, but for testing purposes,
    # private member variables are used to manually add elements to tiles
    generated_elements: BoardElementSet = board._generator_rule.produce_tiles(board)
    if generated_elements is not None:
        for pair in generated_elements.get_element_pairs():
            board.get_tile_at(pair.coordinate).add_game_element(pair.element)

    # Start game
    game.start()
