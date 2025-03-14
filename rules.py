# CONCRETE CLASSES SHOULD NOT GO HERE

from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, NamedTuple, Set

if TYPE_CHECKING:
    from typing import Optional, Union
    from board import Board
    from board_elements import BoardElementSet
    from button_controller import DirectionButton, ActionButton
    from shift_rules import ShiftDirection



class ElementGenerationFailException(BaseException):
    """
    Exception to be raised in the event when a tile is supposed to
    be generated, but fails to fit inside the board. This typically
    happens in games where tiles are actively made (and the player)
    needs to organize them, compared to passive generation where
    tiles tend to be an effect of player actions
    """
    pass


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
    def check_matches(self, board: Board) -> Optional[BoardElementSet]:
        """
        A single rule to check for a match on a board
        :param board: The board to check
        :return: The set of tiles which should be removed.
                 None if no matches were made
        """
        ...


class TileGeneratorRule(ABC):
    """
    An interface defining how a board should try to generate new tile on a single game tick

    Implementing classes must define the `produce_tiles` method, which evaluates
    the coordinates of where new tiles can be placed on the board

    Example:
        If a game requires to fill any empty spots with new tiles, 'produce_tiles'
        should fill any immediate tiles on the top (Ex: Candy Crush).

    Note:
        This rule is only responsible for placing new tiles on the board. It does not
        dictate what happens after tiles are produced as that should be
        handled by another rule.
        In some cases, whether a board has an active tile or not might affect the state of the
        generator rule. This is typically the case for generators which actively make tiles.
        Additionally, depending on the rule, this might throw a ElementGenerationFailException
        in the event where an element set is supposed to generate, but is unable
        to do so.

    """
    @abstractmethod
    def produce_tiles(self, board: Board) -> Optional[BoardElementSet]:
        """
        A single rule to determine where to place tiles on a board

        Returns all game elements which were places, alongside their
        coordinates. In the case where no tiles were placed, returns None

        :param board: The board to check
        :return: A sequence of tiles which were placed, None otherwise
        """
        ...


class UserInputRule(ABC):
    """
    A single rule to determine how the board will handle user input

    Implementing classes must define the `handle_input` method, which affects some
    aspect of the board based on some event
    """

    @abstractmethod
    def handle_input(self, board: Board, *, event: Union[DirectionButton, ActionButton]):
        ...


class UserInputRuleSet(NamedTuple):
    input_rule: UserInputRule
    input_set: Set[DirectionButton | ActionButton]


class TileMovementRule(ABC):
    """
    A single rule to determine how tiles are intended to move

    Implementing classes must define the `move_tiles` method, which moves either static or live tiles
    in a shift direction by some shift amount

    Example:
        In many games, it is typical for elements to fall down by one tile every single game tick.
        There are some exceptions such as in Puzzle Bobble where the launched element goes
        up by one tile every cycle

    Note:
        In some games, there is a live tile which can be controlled by the player. Because
        these element are not tracked by the board until they fall down to the bottom, rules there should
        be special rules which exclusively affect only the board tiles and only the live elements.
        Additionally, for shift values greater than 1, if a tile is not able to shift the entire
        shift distance, then it will move the most it is capable of. For example, if the shift
        distance of one, but after shifting only one tile, an element hits a wall, then it stops
    """
    def set_shift_direction(self, shift_direction: ShiftDirection):
        self._shift_direction = shift_direction

    def set_shift_amount(self, shift_amount: int):
        if shift_amount <= 0:
            raise ValueError(f"shift amount needs to be greater than one, not {shift_amount}")
        self._shift_amount = shift_amount

    @abstractmethod
    def move_tiles(self, board: Board):
        ...
