from typing import TYPE_CHECKING

from generator_rules import FillAllSpotsRule, FillEmptyTopRowSpotsRule
from input_rules import CursorApplyDirectionRule, CursorApplySelectionRule
from match_rules import MatchNOfColorRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board
from board_elements import  GameElement
from provider import UniformRandomElementProvider
from constants import Color
from shift_rules import ShiftStaticTilesRule, ShiftDirection
from user import User

if TYPE_CHECKING:
    pass

# TODO: if anyone wants to, they can make a class for each gem color and
#  make them look pretty
class Gem(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Get the corresponding tkinter color
        from constants import TK_COLOR_MAP
        tile_color = TK_COLOR_MAP.get(self.element_color, "white")
        # Draw a colored rectangle with white border
        canvas.create_rectangle(x1, y1, x2, y2, fill=tile_color, outline="white", width=3)


# class Blocker(GameElement):
#     def __init__(self):
#         self.element_name = 'CandyBlocker'
#         self.supports_color = False
#         self.supports_tile_spawn = False
#         self.supports_tile_move = False
#
#     def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
#         # Draw a gray block with a black border
#         canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="black", width=3)


def apply_bejeweled_rule(board: Board):
    # Set rules dictating how tiles are meant to be filled up
    generate_rule = FillEmptyTopRowSpotsRule()
    provider: UniformRandomElementProvider[GameElement] = UniformRandomElementProvider()
    provider.add_choice(option=Gem(name='GemRed', color=Color.RED))
    provider.add_choice(option=Gem(name='GemOrange', color=Color.ORANGE))
    provider.add_choice(option=Gem(name='GemYellow', color=Color.YELLOW))
    provider.add_choice(option=Gem(name='GemGreen', color=Color.GREEN))
    provider.add_choice(option=Gem(name='GemBlue', color=Color.BLUE))
    provider.add_choice(option=Gem(name='GemPurple', color=Color.PURPLE))
    provider.add_choice(option=Gem(name='GemWhite', color=Color.WHITE))
    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)

    # In games like this, the board is typically full, so a temporary rule is placed
    # The rule is not set since this is not used all the time
    fill_all = FillAllSpotsRule()
    fill_all.set_provider(provider)
    starting_tiles = fill_all.produce_tiles(board)
    if starting_tiles is not None:
        for pair in starting_tiles.get_element_pairs():
            board.get_tile_at(pair.coordinate).add_game_element(pair.element)

    # Movement rules for static tiles
    move_rule = ShiftStaticTilesRule()
    move_rule.set_shift_amount(1)
    move_rule.set_shift_direction(ShiftDirection.DOWN)
    move_rule.enable_tile_movement()
    board.set_static_tile_move_rule(move_rule)

    # User input with cursor management
    board.enable_cursor()
    board.add_user_input_rule(CursorApplyDirectionRule(), input_set={DirectionButton.UP, DirectionButton.DOWN,
                                                                     DirectionButton.LEFT, DirectionButton.RIGHT})
    board.add_user_input_rule(CursorApplySelectionRule(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})

    # Match rules
    match_rule = MatchNOfColorRule()
    match_rule.set_match_length(3)
    board.set_tile_match_rule(match_rule)


if __name__ == '__main__':
    # Constructors
    game = Game()
    board = Board(height=7, width=7)
    user = User.load_from_file('test_user1', password='test_user1')

    controller = KeyboardController()
    controller.set_keybinds(user.get_keyboard_keybinds())

    apply_bejeweled_rule(board)

    # Associated input rules for the board will now be executed from the associated controller
    game.bind(controller, board)

    # tkinter specific
    controller.bind_to_window(game.get_window())

    # Start game
    game.start()
