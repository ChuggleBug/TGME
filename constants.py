from enum import Enum, auto

class Color(Enum):
    DEFAULT = auto()
    WHITE = auto()
    GRAY = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    PURPLE = auto()
    LIGHT_BLUE = auto()
    ORANGE = auto()

TK_COLOR_MAP = {
    Color.DEFAULT: '#FFFFFF',  # White
    Color.WHITE: '#FFFFFF',    # White
    Color.GRAY: '#808080',     # Gray
    Color.BLACK: '#000000',     # Gray
    Color.RED: '#FF0000',      # Red
    Color.GREEN: '#008000',    # Green
    Color.BLUE: '#0000FF',     # Blue
    Color.YELLOW: '#FFFF00',   # Yellow
    Color.PURPLE: '#800080',   # Purple
    Color.LIGHT_BLUE: '#ADD8E6', # Light Blue
    Color.ORANGE: '#FFA500'    # Orange
}
