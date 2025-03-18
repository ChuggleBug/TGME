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
    Color.LIGHT_BLUE: '#01FFFF', # Light Blue
    Color.ORANGE: '#FFA500'    # Orange
}


def darken_color(color: Color, percentage: int) -> str:
    hex_color = TK_COLOR_MAP[color].lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    factor = 1 - (percentage / 100)
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    return f"#{r:02X}{g:02X}{b:02X}"

