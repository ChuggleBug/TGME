from typing import TYPE_CHECKING

from clock import Clock
from generator_rules import FillAllSpotsRule, FillEmptyTopRowSpotsRule, DropElementSetRule
from rules import UserInputRule, TileMatchRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board, Coordinate
from board_elements import RelativeElementSet, BoardElementSet, GameElement
from provider import WeightedRandomElementProvider, UniformRandomElementProvider
from constants import Color
from shift_rules import ShiftStaticTilesRule, ShiftDirection

if TYPE_CHECKING:
    pass


class Candy(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Get the corresponding tkinter color
        from constants import TK_COLOR_MAP
        tile_color = TK_COLOR_MAP.get(self.element_color, "white")
        # Draw a colored rectangle with white border
        canvas.create_rectangle(x1, y1, x2, y2, fill=tile_color, outline="white", width=3)


class Blocker(GameElement):
    def __init__(self):
        self.element_name = 'CandyBlocker'
        self.supports_color = False
        self.supports_tile_spawn = False
        self.supports_tile_move = False

    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Draw a gray block with a black border
        canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="black", width=3)

if __name__ == "__main__":
    # Default original code below
    # Constructors
    game = Game()
    board = Board(height=20, width=20, player_id=5)
    controller = KeyboardController()

    # Set rules dictating how tiles are meant to be filled up
    # You can test out of rules work by changing
    # FillEmptyTopRowSpotsRule to FillAllSpotsRule
    generate_rule = FillEmptyTopRowSpotsRule()
    # Generators rules need element providers
    provider: WeightedRandomElementProvider[GameElement] = WeightedRandomElementProvider()
    provider.add_choice(option=Candy(name='CandyRed', color=Color.RED), weight=25)
    provider.add_choice(option=Candy(name='CandyBlue', color=Color.BLUE), weight=50)
    provider.add_choice(option=Candy(name='CandyGreen', color=Color.GREEN), weight=25)

    move_rule = ShiftStaticTilesRule()
    move_rule.set_shift_amount(1)
    move_rule.set_shift_direction(ShiftDirection.DOWN)
    board.set_static_tile_move_rule(move_rule)

    # for this example only, a blocker was added
    # a blocker prevents the spawning of candies when something tries
    # to spawn on it
    board.get_tile_at(Coordinate(0, 0)).add_game_element(Blocker())

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)

    # Associated input rules for the board will now be executed from the associated controller
    game.bind(controller, board)

    # tkinter specific
    controller.bind_to_window(game.get_window())

    Clock.set_game(game)
    Clock.set_update_rate(0.5)

    # Start game
    game.start()
