
from __future__ import annotations
from typing import TYPE_CHECKING, Union

from clock import Clock
from generator_rules import DropElementSetRule
from rules import UserInputRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board, Coordinate
from board_elements import RelativeElementSet, GameElement
from provider import RandomRepeatingQueueElementProvider
from constants import Color
from shift_rules import ShiftLiveTilesRule, ShiftDirection, ShiftStaticTilesRule

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

class LeftRightHandler(UserInputRule):
    VALID_INPUT_SET = frozenset([ShiftDirection.LEFT, ShiftDirection.RIGHT])

    def __init__(self):
        self._live_shifter = ShiftLiveTilesRule()
        self._live_shifter.set_shift_amount(1)

    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        if event not in LeftRightHandler.VALID_INPUT_SET:
            return

        if event == DirectionButton.LEFT:
            self._live_shifter.set_shift_direction(ShiftDirection.LEFT)
        elif event == DirectionButton.RIGHT:
            self._live_shifter.set_shift_direction(ShiftDirection.RIGHT)

        self._live_shifter.move_tiles(board)


class DefaultHandler(UserInputRule):

    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        pass


if __name__ == '__main__':
    game = Game()
    board = Board(height=7, width=9, player_id=5)
    controller = KeyboardController()

    # User input rules
    board.add_user_input_rule(LeftRightHandler(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT})
    board.add_user_input_rule(DefaultHandler(), input_set={DirectionButton.UP, DirectionButton.DOWN,
                                                           ActionButton.PRIMARY, ActionButton.SECONDARY})

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

    # Tile Movement Rule
    static_move_down_rule = ShiftStaticTilesRule()
    static_move_down_rule.set_shift_amount(1)
    static_move_down_rule.set_shift_direction(ShiftDirection.DOWN)
    static_move_down_rule.enable_tile_movement()
    board.set_static_tile_move_rule(static_move_down_rule)

    live_move_horizontal_rule = ShiftLiveTilesRule()
    live_move_horizontal_rule.set_shift_amount(1)
    live_move_horizontal_rule.set_shift_direction(ShiftDirection.DOWN)
    live_move_horizontal_rule.enable_tile_movement()
    board.set_live_tile_move_rule(live_move_horizontal_rule)

    # Game visual setup
    game.bind(controller, board)
    # tkinter specific
    controller.bind_to_window(game.get_window())

    # while True:
    #     board.update()

    Clock.set_game(game)
    Clock.set_update_rate(2)

    game.start()


