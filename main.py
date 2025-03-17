from typing import TYPE_CHECKING

from generator_rules import FillEmptyTopRowSpotsRule, DropElementSetRule
from input_rules import HorizontalShiftLiveTileRule, DownwardsShiftLiveTileRule, RotateLiveTilesRule
from game import Game
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board
from board_elements import RelativeElementSet, GameElement, Coordinate
from provider import RandomRepeatingQueueElementProvider
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


def set_candy_crush_generation(board: Board):
    # Set rules dictating how tiles are meant to be filled up
    # You can test out of rules work by changing
    # FillEmptyTopRowSpotsRule to FillAllSpotsRule
    generate_rule = FillEmptyTopRowSpotsRule()
    # Generators rules need element providers
    provider: RandomRepeatingQueueElementProvider[GameElement] = RandomRepeatingQueueElementProvider()
    provider.add_choice(option=Candy(name='CandyRed', color=Color.RED), weight=25)
    provider.add_choice(option=Candy(name='CandyBlue', color=Color.BLUE), weight=50)
    provider.add_choice(option=Candy(name='CandyGreen', color=Color.GREEN), weight=25)

    # for this example only, a blocker was added
    # a blocker prevents the spawning of candies when something tries
    # to spawn on it
    board.get_tile_at(Coordinate(0, 0)).add_game_element(Blocker())

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)


def set_tetris_generation(board: Board, game: Game = None, controller: KeyboardController = None, drop_interval: int = 1000):
    """
    board: The game board to set up
    game: The Game instance (optional, for gravity)
    controller: The KeyboardController (optional, for input)
    drop_interval: Time in ms between automatic drops (default: 1000ms = 1 second)
    """
    # Set up the piece generator
    generate_rule = DropElementSetRule()
    provider: RandomRepeatingQueueElementProvider[RelativeElementSet] = RandomRepeatingQueueElementProvider()

    # Add all the different Tetris pieces to the provider
    for piece in create_tetris_pieces():
        provider.add_choice(piece)

    generate_rule.set_provider(provider)
    board.set_tile_generator_rule(generate_rule)
    
    # Set up input rules for movement if controller is provided
    if controller:
        # Add user input rules for Tetris controls
        board.add_user_input_rule(DownwardsShiftLiveTileRule(), input_set={DirectionButton.UP, DirectionButton.DOWN})
        board.add_user_input_rule(HorizontalShiftLiveTileRule(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT})
        board.add_user_input_rule(RotateLiveTilesRule(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})
        
        # Bind controller to the board if game is provided
        if game:
            game.bind(controller, board)
    
    # Set up gravity if game is provided
    if game:
        # Create and set the gravity rule with the specified drop interval
        game.set_gravity_rule(drop_interval=drop_interval)

        print("Tetris game set up successfully!")
        print("Controls:")
        print("- Left/Right Arrows: Move block left/right")
        print("- Down Arrow: Move block down faster")
        print("- Block automatically drops one cell per second")


def create_tetris_pieces():
    """
    Create a variety of standard Tetris pieces with different shapes and colors.
    Returns a list of RelativeElementSet objects representing different pieces.
    """
    pieces = []
    
    # I-piece (long bar) - Cyan
    cyan_tile = TetrisTile(name='CyanTetrisTile', color=Color.LIGHT_BLUE)
    i_piece = RelativeElementSet()
    i_piece.add_element(element=cyan_tile, coordinate=Coordinate(0, 0))
    i_piece.add_element(element=cyan_tile, coordinate=Coordinate(0, 1))
    i_piece.add_element(element=cyan_tile, coordinate=Coordinate(0, 2))
    i_piece.add_element(element=cyan_tile, coordinate=Coordinate(0, 3))
    pieces.append(i_piece)
    
    # O-piece (square) - Yellow
    yellow_tile = TetrisTile(name='YellowTetrisTile', color=Color.YELLOW)
    o_piece = RelativeElementSet()
    o_piece.add_element(element=yellow_tile, coordinate=Coordinate(0, 0))
    o_piece.add_element(element=yellow_tile, coordinate=Coordinate(1, 0))
    o_piece.add_element(element=yellow_tile, coordinate=Coordinate(0, 1))
    o_piece.add_element(element=yellow_tile, coordinate=Coordinate(1, 1))
    pieces.append(o_piece)
    
    # T-piece - Purple
    purple_tile = TetrisTile(name='PurpleTetrisTile', color=Color.PURPLE)
    t_piece = RelativeElementSet()
    t_piece.add_element(element=purple_tile, coordinate=Coordinate(1, 0))
    t_piece.add_element(element=purple_tile, coordinate=Coordinate(0, 1))
    t_piece.add_element(element=purple_tile, coordinate=Coordinate(1, 1))
    t_piece.add_element(element=purple_tile, coordinate=Coordinate(2, 1))
    pieces.append(t_piece)
    
    # L-piece - Orange
    red_tile = TetrisTile(name='RedTetrisTile', color=Color.ORANGE)
    l_piece = RelativeElementSet()
    l_piece.add_element(element=red_tile, coordinate=Coordinate(2, 0))
    l_piece.add_element(element=red_tile, coordinate=Coordinate(0, 1))
    l_piece.add_element(element=red_tile, coordinate=Coordinate(1, 1))
    l_piece.add_element(element=red_tile, coordinate=Coordinate(2, 1))
    pieces.append(l_piece)
    
    # J-piece - Blue
    green_tile = TetrisTile(name='GreenTetrisTile', color=Color.BLUE)
    j_piece = RelativeElementSet()
    j_piece.add_element(element=green_tile, coordinate=Coordinate(0, 0))
    j_piece.add_element(element=green_tile, coordinate=Coordinate(0, 1))
    j_piece.add_element(element=green_tile, coordinate=Coordinate(1, 1))
    j_piece.add_element(element=green_tile, coordinate=Coordinate(2, 1))
    pieces.append(j_piece)
    
    return pieces


if __name__ == "__main__":
    # === TETRIS GAME CONFIGURATION ===
    # You can modify these settings to change the game
    board_size = (15, 10)  # (height, width) - Change this to adjust board size
    drop_speed = 1000      # Time in milliseconds between drops (1000 = 1 second)
    add_obstacles = False   # Set to False to remove obstacles
    
    # === GAME INITIALIZATION ===
    print("=== STARTING TETRIS GAME ===")
    
    # Create game components
    game = Game()
    board = Board(height=board_size[0], width=board_size[1])
    controller = KeyboardController()
    
    # Bind controller to window
    controller.bind_to_window(game.get_window())
    
    # Add a floor at the bottom to prevent pieces from falling through
    if add_obstacles:
        print("Adding floor and obstacles...")
        yellow_candy = Candy(name="YellowCandy", color=Color.YELLOW)
        
        # Add a floor at the bottom
        for x in range(board.get_width()):
            board.get_tile_at(Coordinate(x, board.get_height()-1)).add_game_element(yellow_candy)
        
        # Add some obstacles
        for x in range(3, 7):
            board.get_tile_at(Coordinate(x, board.get_height()-2)).add_game_element(yellow_candy)
    
    # Set up Tetris game with all functionality
    set_tetris_generation(board, game, controller, drop_speed)
    
    # Start the game
    print(f"Board size: {board_size[0]}x{board_size[1]}")
    game.start()
