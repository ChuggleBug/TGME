from typing import TYPE_CHECKING

from generator_rules import FillAllSpotsRule, FillEmptyTopRowSpotsRule, DropElementSetRule
from rules import UserInputRule, TileMatchRule
from game import Game
from gravity_rules import DownwardGravityRule
from button_controller import KeyboardController, DirectionButton, ActionButton
from board import Board
from board_elements import RelativeElementSet, BoardElementSet, GameElement, Coordinate
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

class LeftRightInput(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if not board.has_live_tiles():
            return
            
        # Get the direction to move
        direction = None
        if event == DirectionButton.LEFT:
            print("Moving Tetris block left")
            direction = Coordinate(-1, 0)
        elif event == DirectionButton.RIGHT:
            print("Moving Tetris block right")
            direction = Coordinate(1, 0)
            
        if direction:
            # Try to move the live tiles in the specified direction
            self._move_live_tiles(board, direction)
    
    def _move_live_tiles(self, board: Board, direction: Coordinate):
        """Move the live tiles if the move is valid."""
        live_tiles = board.get_live_tiles()
        # Create a new set with the moved positions
        new_positions = BoardElementSet()
        
        # Check if the move is valid (no collisions)
        can_move = True
        for pair in live_tiles.get_element_pairs():
            new_pos = pair.coordinate + direction
            
            # Check boundaries
            if (new_pos.x < 0 or new_pos.x >= board.get_width() or 
                new_pos.y < 0 or new_pos.y >= board.get_height()):
                can_move = False
                break
                
            # Check collision with static elements
            tile = board.get_tile_at(new_pos)
            if tile and tile.has_elements():
                # If there's any element in this tile, we can't move there
                can_move = False
                break
        
        # If move is valid, update live tiles positions
        if can_move:
            for pair in live_tiles.get_element_pairs():
                new_pos = pair.coordinate + direction
                new_positions.add_element(pair.element, new_pos)
            
            # Update the board's live tiles
            board.set_live_tile(new_positions)

class UpDownInput(UserInputRule):
    def handle_input(self, board: Board, *, event):
        if not board.has_live_tiles():
            return
            
        # Tetris pieces should only move down, not up
        if event == DirectionButton.DOWN:
            print("Moving Tetris block down")
            self._move_live_tiles_down(board)
        elif event == DirectionButton.UP:
            print("Up movement not allowed in Tetris")
    
    def _move_live_tiles_down(self, board: Board):
        """Move the live tiles down if possible."""
        direction = Coordinate(0, 1)  # Down
        live_tiles = board.get_live_tiles()
        new_positions = BoardElementSet()
        
        # Check if downward movement is valid
        can_move = True
        for pair in live_tiles.get_element_pairs():
            new_pos = pair.coordinate + direction
            
            # Check if new position is out of bounds
            if new_pos.y >= board.get_height():
                can_move = False
                break
                
            # Check collision with static elements
            tile = board.get_tile_at(new_pos)
            if tile and tile.has_elements():
                # If there's any element in this tile, we can't move there
                can_move = False
                break
        
        # If can move down, update positions
        if can_move:
            for pair in live_tiles.get_element_pairs():
                new_pos = pair.coordinate + direction
                new_positions.add_element(pair.element, new_pos)
            
            # Update the board's live tiles
            board.set_live_tile(new_positions)
        else:
            # If can't move down, convert live tiles to static tiles
            self._lock_live_tiles(board)
    
    def _lock_live_tiles(self, board: Board):
        """Convert live tiles to static tiles when they can't move down anymore."""
        if board.has_live_tiles():
            live_tiles = board.get_live_tiles()
            
            # Add each live tile to the static board
            for pair in live_tiles.get_element_pairs():
                board.get_tile_at(pair.coordinate).add_game_element(pair.element)
            
            # Clear the live tiles
            board.set_live_tile(BoardElementSet())
            
            # Generate new tetris piece
            new_piece = generate_centered_piece(board)
            if new_piece:
                board.set_live_tile(new_piece)

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
        board.set_tile_match_rule(TestTileMatch())
        board.add_user_input_rule(UpDownInput(), input_set={DirectionButton.UP, DirectionButton.DOWN})
        board.add_user_input_rule(LeftRightInput(), input_set={DirectionButton.LEFT, DirectionButton.RIGHT})
        board.add_user_input_rule(ActionInput(), input_set={ActionButton.PRIMARY, ActionButton.SECONDARY})
        
        # Bind controller to the board if game is provided
        if game:
            game.bind(controller, board)
    
    # Set up gravity if game is provided
    if game:
        # Create and set the gravity rule with the specified drop interval
        game.set_gravity_rule(drop_interval=drop_interval)
        
        # Generate the initial tetris piece
        new_piece = generate_centered_piece(board)
        if new_piece:
            board.set_live_tile(new_piece)
            
        print("Tetris game set up successfully!")
        print("Controls:")
        print("- Left/Right Arrows: Move block left/right")
        print("- Down Arrow: Move block down faster")
        print("- Block automatically drops one cell per second")


def generate_centered_piece(board: Board):
    """
    Generate a new Tetris piece and center it at the top of the board.
    Returns the centered piece as a BoardElementSet or None if generation failed.
    """
    try:
        # Try to get a piece from the generator rule
        generated_elements = board._generator_rule.produce_tiles(board)
        if generated_elements is not None and len(generated_elements.get_element_pairs()) > 0:
            # Place the piece at the top center of the board
            centered_piece = BoardElementSet()
            center_x = board.get_width() // 2 - 1
            
            # Check for collisions with existing blocks
            collision = False
            for pair in generated_elements.get_element_pairs():
                new_x = center_x + pair.coordinate.x
                new_y = pair.coordinate.y
                
                # Check if position is valid
                if (new_x < 0 or new_x >= board.get_width() or 
                    new_y < 0 or new_y >= board.get_height()):
                    collision = True
                    break
                
                # Check if position is already occupied
                tile = board.get_tile_at(Coordinate(new_x, new_y))
                if tile and tile.has_elements():
                    collision = True
                    break
            
            # If no collision, create the centered piece
            if not collision:
                for pair in generated_elements.get_element_pairs():
                    new_x = center_x + pair.coordinate.x
                    new_y = pair.coordinate.y
                    centered_piece.add_element(pair.element, Coordinate(new_x, new_y))
                
                print("New piece generated")
                return centered_piece
            else:
                print("Collision detected when placing new piece - game might be over")
                return None
        else:
            print("Generator didn't produce pieces, creating fallback piece")
            # Create a fallback piece using one of our predefined pieces
            import random
            pieces = create_tetris_pieces()
            fallback_piece = random.choice(pieces)
            
            # Center the fallback piece at the top of the board
            centered_piece = BoardElementSet()
            center_x = board.get_width() // 2 - 1
            
            # Check for collisions with existing blocks
            collision = False
            for pair in fallback_piece.get_element_pairs():
                new_x = center_x + pair.coordinate.x
                new_y = pair.coordinate.y
                
                # Check if position is valid
                if (new_x < 0 or new_x >= board.get_width() or 
                    new_y < 0 or new_y >= board.get_height()):
                    collision = True
                    break
                
                # Check if position is already occupied
                tile = board.get_tile_at(Coordinate(new_x, new_y))
                if tile and tile.has_elements():
                    collision = True
                    break
            
            # If no collision, create the centered piece
            if not collision:
                for pair in fallback_piece.get_element_pairs():
                    new_x = center_x + pair.coordinate.x
                    new_y = pair.coordinate.y
                    centered_piece.add_element(pair.element, Coordinate(new_x, new_y))
                
                return centered_piece
            else:
                print("Collision detected when placing fallback piece - game over")
                return None
    except Exception as e:
        print(f"Error generating new piece: {e}")
        return None


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
    board = Board(height=board_size[0], width=board_size[1], player_id=1)
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
