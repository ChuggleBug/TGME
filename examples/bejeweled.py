from typing import TYPE_CHECKING
import math

import sys
import os

from condition_rules import CheckIfMatchPossibleRule

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator_rules import FillAllSpotsRule, FillEmptyTopRowSpotsRule
from input_rules import CursorApplyDirectionRule, CursorApplySelectionRule
from match_rules import MatchNOfColorRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board
from board_elements import  GameElement
from provider import UniformRandomElementProvider
from constants import Color, darken_color, TK_COLOR_MAP
from shift_rules import ShiftStaticTilesRule, ShiftDirection
from user import User

if TYPE_CHECKING:
    pass


class Gem(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Get the corresponding tkinter color
        tile_color = TK_COLOR_MAP.get(self.element_color, "white")
        if self.element_name == 'GemRed':
            #Diamond
            tile_width = x2 - x1
            tile_height = y2 - y1
            center_x = x1 + tile_width // 2
            center_y = y1 + tile_height // 2
            points = [
                (center_x, y1 + 5),
                (x2 - 5, center_y),
                (center_x, y2 - 5), 
                (x1 + 5, center_y)
            ]
            canvas.create_polygon(points, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        elif self.element_name == 'GemOrange':
            #Circle
            canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        elif self.element_name == 'GemGreen':
            #Triangle
            center_x = (x1 + x2) // 2
            points = [
                (center_x, y1 + 10),
                (x1 + 10, y2 - 10),
                (x2 - 10, y2 - 10)
            ]
            canvas.create_polygon(points, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        elif self.element_name == 'GemBlue':
            #Pentagon
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            radius = min((x2 - x1), (y2 - y1)) // 2.5
            points = []
            for i in range(5):
                angle = math.radians(90 + i * 72)
                px = center_x + radius * math.cos(angle)
                py = center_y - radius * math.sin(angle)
                points.append((px, py))
            canvas.create_polygon(points, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        elif self.element_name == 'GemPurple':
            #Upsidedown Triangle
            center_x = (x1 + x2) // 2
            points = [
                (x1 + 10, y1 + 10),
                (x2 - 10, y1 + 10),
                (center_x, y2 - 10)
            ]
            canvas.create_polygon(points, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        elif self.element_name == 'GemWhite':
            # Octagon
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            radius = min((x2 - x1), (y2 - y1)) // 2.5
            points = []
            for i in range(6):
                angle = math.radians(90 + i * 60)
                px = center_x + radius * math.cos(angle)
                py = center_y - radius * math.sin(angle)
                points.append((px, py))
            canvas.create_polygon(points, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=2)
        else:
            #Square
            canvas.create_rectangle(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=tile_color, outline=darken_color(self.element_color, percentage=25), width=3)

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

    board.add_game_condition_rule(CheckIfMatchPossibleRule())

if __name__ == '__main__':
    game = Game()

    board1 = Board(height=10, width=10)
    apply_bejeweled_rule(board1)
    game.add_board(board1)

    board2 = Board(height=10, width=10)
    apply_bejeweled_rule(board2)
    game.add_board(board2)

    user1 = User.load_from_file('test_user1', password='test_user1')
    user2 = User.load_from_file('test_user2', password='test_user2')

    controller1 = KeyboardController()
    controller1.set_keybinds(user1.get_keyboard_keybinds())
    # tkinter specific
    controller1.bind_to_board_window(game.get_window())

    controller2 = KeyboardController()
    controller2.set_keybinds(user2.get_keyboard_keybinds())
    # tkinter specific
    controller2.bind_to_board_window(game.get_window())

    game.bind(controller1, board_index=0)
    game.bind(controller2, board_index=1)
    game.start()
