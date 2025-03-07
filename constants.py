from enum import Enum, auto

class Color(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    PURPLE = auto()
    WHITE = auto()
    DEFAULT = auto()

TK_COLOR_MAP = \
    {Color.DEFAULT: 'white',
     Color.WHITE: 'white',
     Color.RED: 'red',
     Color.GREEN: 'green',
     Color.BLUE: 'blue',
     Color.YELLOW: 'yellow',
     Color.PURPLE: 'purple'
     }