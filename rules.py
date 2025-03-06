
from __future__ import annotations
from abc import ABC, abstractmethod

import random
from typing import TYPE_CHECKING

from gameboard import Coordinate, GameElement

if TYPE_CHECKING:
    from typing import Optional, Union
    from gameboard import Board, ElementSet
    from button_controller import DirectionButton, ActionButton


# Don't Use. Will ask professor about how to use this design pattern
class Rule(ABC):
    """
    Marker interface to indicate that a class is a rule.

    Note:
        The actual instance should be determined at runtime
    """
    pass

class TileMatchRule(ABC):
    """
    An interface defining how a board should check for tile matches.

    Implementing classes must define the `check_matches` method, which evaluates
    the current state of the board and detects matches.

    Example:
        If a game requires filling an entire row to trigger a match, the `check_matches`
        method should detect when a row is full and clear it (Ex: Tetris).

    Note:
        This rule is only responsible for detecting matches. Clearing should be done by some other
        rule of the board itself.
    """

    @abstractmethod
    def check_matches(self, board: Board) -> Optional[ElementSet]:
        """
        A single rule to check for a match on a board
        :param board: The board to check
        :return: The set of tiles which should be removed.
                 None if no matches were made
        """
        ...


# TODO: Should this return an Iterable consisting of where the tiles
# TODO: were place, or just directly modify the board itself (or both)?
class TileGeneratorRule(ABC):
    """
    An interface defining a board should try to generate new tile on a single game tick

    Implementing classes must define the `produce_tiles` method, which evaluates
    the coordinates of where new tiles can be placed on the board

    Example:
        If a game requires to fill any empty spots with new tiles, 'produce_tiles'
        should fill any immediate tiles on the top (Ex: Candy Crush).

    Note:
        This rule is only responsible for placing new tiles on the board. It does not
        dictate what happens after tiles are produced as that should be
        handled by another rule.
    """
    @abstractmethod
    def produce_tiles(self, board: Board) -> Optional[ElementSet]:
        """
        A single rule to determine where to place tiles on a board

        Returns all game elements which were places, alongside their
        coordinates. In the case where no tiles were placed, returns None

        :param board: The board to check
        :return: A sequence of tiles which were placed, None otherwise
        """
        ...

class FillEmptySpots(TileGeneratorRule):
    def produce_tiles(self, board: Board) -> Optional[ElementSet]:
        generated_tiles = ElementSet()
        for row in range(board.get_rows()):
            for col in range(board.get_cols()):
                tile = board._tiles.get_copy(row, col)
                if tile.is_empty():
                    new_tile = GameElement(type_=random.choice(["R", "G", "B", "Y"]))
                    tile._elements.append(new_tile)
                    generated_tiles.add_element(new_tile, Coordinate(row, col))
                #print(f"{tile._elements[0].type} ({row}, {col})")
        return generated_tiles if len(generated_tiles.get_elements()) > 0 else None

class UserInputRule(ABC):
    """
    A single rule to determine how the board will handle user input

    A rule is given a
    """

    @abstractmethod
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        ...
