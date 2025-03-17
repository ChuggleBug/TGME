
from __future__ import annotations
from typing import TYPE_CHECKING

from game import Game
from board import Board
from board_elements import GameElement, RelativeElementSet, Coordinate
from button_controller import KeyboardController, DirectionButton, ActionButton

from input_rules import HorizontalShiftLiveTileRule, DownwardsShiftLiveTileRule, RotateLiveTilesRule, DoNothingRule
from match_rules import MatchARowRule, ShiftToFillRowEventRule
from generator_rules import DropElementSetRule
from provider import RandomRepeatingQueueElementProvider
from gravity_rules import DownwardGravityRule
from constants import Color
from user import User

if TYPE_CHECKING:
    pass


class TetrisTile(GameElement):
    def __init__(self, *, name: str, color: Color):
        self.element_name = name
        self.element_color = color

    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Get the corresponding tkinter color
        from constants import TK_COLOR_MAP
        tile_color = TK_COLOR_MAP.get(self.element_color, "white")
        # Draw a colored rectangle with black border
        canvas.create_rectangle(x1, y1, x2, y2, fill=tile_color, outline="black", width=3)
        # Add a small indicator in the center to distinguish it from candy
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        size = min(x2 - x1, y2 - y1) // 4
        canvas.create_oval(center_x - size, center_y - size,
                           center_x + size, center_y + size,
                           fill="white")

light_blue_tile = TetrisTile(name="LightBlueTile", color=Color.LIGHT_BLUE)
yellow_tile = TetrisTile(name="YellowTile", color=Color.YELLOW)
purple_tile = TetrisTile(name="PurpleTile", color=Color.PURPLE)
green_tile = TetrisTile(name="GreenTile", color=Color.GREEN)
red_tile = TetrisTile(name="RedTile", color=Color.RED)
blue_tile = TetrisTile(name="BlueTile", color=Color.BLUE)
orange_tile = TetrisTile(name="OrangeTile", color=Color.ORANGE)

line_block = RelativeElementSet()
line_block.add_element(light_blue_tile, Coordinate(0, 0))
line_block.add_element(light_blue_tile, Coordinate(0, 1))
line_block.add_element(light_blue_tile, Coordinate(0, 2))
line_block.add_element(light_blue_tile, Coordinate(0, 3))

o_block = RelativeElementSet()
o_block.add_element(yellow_tile, Coordinate(0, 0))
o_block.add_element(yellow_tile, Coordinate(0, 1))
o_block.add_element(yellow_tile, Coordinate(1, 0))
o_block.add_element(yellow_tile, Coordinate(1, 1))

t_block = RelativeElementSet()
t_block.add_element(purple_tile, Coordinate(1, 0))
t_block.add_element(purple_tile, Coordinate(0, 1))
t_block.add_element(purple_tile, Coordinate(1, 1))
t_block.add_element(purple_tile, Coordinate(2, 1))

s_block = RelativeElementSet()
s_block.add_element(green_tile, Coordinate(1, 0))
s_block.add_element(green_tile, Coordinate(2, 0))
s_block.add_element(green_tile, Coordinate(0, 1))
s_block.add_element(green_tile, Coordinate(1, 1))

z_block = RelativeElementSet()
z_block.add_element(red_tile, Coordinate(0, 0))
z_block.add_element(red_tile, Coordinate(1, 0))
z_block.add_element(red_tile, Coordinate(1, 1))
z_block.add_element(red_tile, Coordinate(2, 1))

j_block = RelativeElementSet()
j_block.add_element(blue_tile, Coordinate(1, 0))
j_block.add_element(blue_tile, Coordinate(1, 1))
j_block.add_element(blue_tile, Coordinate(1, 2))
j_block.add_element(blue_tile, Coordinate(0, 2))

# not to be confused with the line block (4 long piece)
# meant to look like "L"
l_block = RelativeElementSet()
l_block.add_element(orange_tile, Coordinate(0, 0))
l_block.add_element(orange_tile, Coordinate(0, 1))
l_block.add_element(orange_tile, Coordinate(0, 2))
l_block.add_element(orange_tile, Coordinate(1, 2))


def apply_tetris_rule(board: Board):
    # User input rules
    board.add_user_input_rule(HorizontalShiftLiveTileRule(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT})
    board.add_user_input_rule(DownwardsShiftLiveTileRule(), input_set={DirectionButton.DOWN})
    board.add_user_input_rule(DoNothingRule(), input_set={DirectionButton.UP})
    board.add_user_input_rule(RotateLiveTilesRule(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})

    # Tile matching rules
    match_rule = MatchARowRule()
    board.set_tile_match_rule(match_rule)

    # Match event rules
    match_event = ShiftToFillRowEventRule()
    board.add_match_event_rule(match_event)

    # Board tile generation rules
    generator = DropElementSetRule()
    tetris_tile_provider = RandomRepeatingQueueElementProvider()
    tetris_tile_provider.add_choice(line_block)
    tetris_tile_provider.add_choice(o_block)
    tetris_tile_provider.add_choice(t_block)
    tetris_tile_provider.add_choice(s_block)
    tetris_tile_provider.add_choice(z_block)
    tetris_tile_provider.add_choice(l_block)
    tetris_tile_provider.add_choice(j_block)
    generator.set_provider(tetris_tile_provider)
    board.set_tile_generator_rule(generator)

    # Tile Gravity Rule
    gravity_rule = DownwardGravityRule()
    gravity_rule.set_update_rate(time_ms=2500)
    board.set_gravity_rule(gravity_rule)


if __name__ == '__main__':
    game = Game()

    # TODO: typically the tetris board is 40x10, but the GUI
    #  gets weird for larger sizes. Maybe someone can fix that?
    board = Board(height=30, width=10)
    apply_tetris_rule(board)
    user = User.load_from_file('test_user1', password='test_user1')

    controller = KeyboardController()
    controller.set_keybinds(user.get_keyboard_keybinds())

    # Game visual setup
    game.bind(controller, board)

    # tkinter specific
    controller.bind_to_window(game.get_window())

    game.start()


