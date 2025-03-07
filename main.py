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
        
    def draw(self, canvas, x1: int, y1: int, x2: int, y2: int):
        # Draw a gray block with a black border
        canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="black", width=3)


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

    purple_tile = TetrisTile(name='PurpleTetrisTile', color=Color.PURPLE)
    yellow_tile = TetrisTile(name='YellowTetrisTile', color=Color.YELLOW)
    blue_tile = TetrisTile(name='LightBlueTetrisTile', color=Color.BLUE)

    t_block = RelativeElementSet()
    t_block.add_element(element=purple_tile, coordinate=Coordinate(1,0))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(0, 1))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(1, 1))
    t_block.add_element(element=purple_tile, coordinate=Coordinate(2, 1))

    o_block = RelativeElementSet()
    o_block.add_element(element=yellow_tile, coordinate=Coordinate(0, 0))
    o_block.add_element(element=yellow_tile, coordinate=Coordinate(0, 1))
    o_block.add_element(element=yellow_tile, coordinate=Coordinate(1, 0))
    o_block.add_element(element=yellow_tile, coordinate=Coordinate(1, 1))

    l_block = RelativeElementSet()
    l_block.add_element(element=blue_tile, coordinate=Coordinate(0, 0))
    l_block.add_element(element=blue_tile, coordinate=Coordinate(0, 1))
    l_block.add_element(element=blue_tile, coordinate=Coordinate(0, 2))
    l_block.add_element(element=blue_tile, coordinate=Coordinate(0, 3))

    provider.add_choice(t_block)
    provider.add_choice(o_block)
    provider.add_choice(l_block)

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)


def test_board_sizes(size_to_test):
    """
    Test function to create a board of specified size and render it.
    
    Args:
        size_to_test: Tuple of (height, width) to test
    """
    # Create game components
    game = Game()
    board = Board(height=size_to_test[0], width=size_to_test[1], player_id=5)
    controller = KeyboardController()
    
    # Set basic rules
    board.set_tile_match_rule(TestTileMatch())
    board.add_user_input_rule(UpDownInput(), input_set={DirectionButton.UP, DirectionButton.DOWN})
    board.add_user_input_rule(LeftRightInput(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT})
    board.add_user_input_rule(ActionInput(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})
    
    # Bind controller and board to the game
    game.bind(controller, board)
    controller.bind_to_window(game.get_window())
    
    # Generate some sample tiles
    set_tetris_generation(board)
    generated_elements = board._generator_rule.produce_tiles(board)
    if generated_elements is not None:
        for pair in generated_elements.get_element_pairs():
            board.get_tile_at(pair.coordinate).add_game_element(pair.element)
    
    # Start the game
    print(f"Testing board size: {size_to_test[0]}x{size_to_test[1]}")
    game.start()


if __name__ == "__main__":
    # Uncomment ONE of these lines to test different board sizes
    #test_board_sizes((5, 5))     # Regular square board (default)
    #test_board_sizes((10, 10))   # Larger square board 
    #test_board_sizes((3, 15))    # Very wide rectangular board
    #test_board_sizes((15, 3))    # Very tall rectangular board
    
    # Default original code below
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

    # This can be swapped with the other generated in this file
    set_tetris_generation(board)

    # This is not good practice, but for testing purposes,
    # private member variables are used to manually add elements to tiles
    generated_elements: BoardElementSet = board._generator_rule.produce_tiles(board)
    if generated_elements is not None:
        for pair in generated_elements.get_element_pairs():
            board.get_tile_at(pair.coordinate).add_game_element(pair.element)

    # Technically, the viewing of live tiles should be handled by the renderer
    # for this example, live lives (if any) are simply appended to the board itself
    if board.has_live_tiles():
        for pair in board.get_live_tiles().get_element_pairs():
            board.get_tile_at(pair.coordinate).add_game_element(pair.element)

    # Start game
    game.start()
