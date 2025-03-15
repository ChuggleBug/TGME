from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

from structures import Matrix
from rules import UserInputRuleSet

if TYPE_CHECKING:
    from typing import List, Set, Optional, Iterable, Any
    from button_controller import DirectionButton, ActionButton
    from board_elements import GameElement, ElementSet, BoardElementSet
    from shift_rules import ShiftDirection
    from rules import TileMatchRule, TileGeneratorRule, TileMovementRule, UserInputRule

@dataclass
class Coordinate:
    x: int
    y: int

    def __add__(self, other: Any) -> Coordinate:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return Coordinate(self.x + other.x, self.y + other.y)

class TileElement:
    def __init__(self):
        self._elements: List[GameElement] = []

    def can_support_tile_spawn(self):
        """
        Indicates that a tile can have a new element spawned inside of it
        """
        return all(map(lambda e: e.supports_tile_spawn, self._elements))

    def can_support_move(self):
        """
        Indicates that has the capability to move. Tiles typically are blocked
        from moving by
        """
        return all(map(lambda e: e.supports_tile_move, self._elements))

    def can_move_through(self):
        return all(map(lambda e:e.supports_move_through, self._elements))

    def add_game_element(self, element: GameElement):
        self._elements.append(element)

    def has_elements(self) -> bool:
        return len(self._elements) > 0

    def __repr__(self):
        return f"TileElement(size={len(self._elements)}, contents={self._elements})"

    def get_elements(self) -> List[GameElement]:
        """
        Returns the list of GameElements in this tile.
        Elements at lower indices are drawn on top of elements at higher indices.
        """
        return self._elements.copy()  # Return a copy to prevent external modification

class Board:
    def __init__(self, height: int, width: int, player_id: int):
        self._tiles: Matrix[TileElement] = Matrix(rows=height, cols=width, initializer=lambda: TileElement())
        self._match_rule: Optional[TileMatchRule] = None
        self._generator_rule: Optional[TileGeneratorRule] = None
        self._live_tiles: Optional[ElementSet] = None
        self._input_rules: List[UserInputRuleSet] = []
        self._static_move_rule: Optional[TileMovementRule] = None
        self._live_move_rule: Optional[TileMovementRule] = None
        self._player_id = player_id

    def get_player_id(self):
       return self._player_id

    def get_live_tiles(self) -> Optional[BoardElementSet]:
        return self._live_tiles

    def set_live_tile(self, live_tiles: Optional[BoardElementSet]):
        self._live_tiles = live_tiles

    def has_live_tiles(self) -> bool:
        return self._live_tiles is not None

    def set_tile_match_rule(self, match_rule: TileMatchRule):
        self._match_rule = match_rule

    def set_tile_generator_rule(self, generator_rule: TileGeneratorRule):
        self._generator_rule = generator_rule

    def add_user_input_rule(self, input_rule: UserInputRule, *, input_set: Set[DirectionButton | ActionButton]):
        self._input_rules.append(UserInputRuleSet(input_rule, input_set))

    def set_static_tile_move_rule(self, move_rule: TileMovementRule):
        self._static_move_rule = move_rule

    def get_static_tile_move_direction(self) -> Optional[ShiftDirection]:
        return self._static_move_rule.get_shift_direction() if self._static_move_rule is not None else None

    def set_live_tile_move_rule(self, move_rule: TileMovementRule):
        self._live_move_rule = move_rule

    def get_live_tile_move_direction(self) -> Optional[ShiftDirection]:
        return self._live_move_rule.get_shift_direction() if self._live_move_rule is not None else None

    def get_user_input_rules(self) -> Iterable[UserInputRuleSet]:
        return self._input_rules

    def get_height(self) -> int:
        return self._tiles.rows

    def get_width(self) -> int:
        return self._tiles.cols

    def get_tile_at(self, coordinate: Coordinate) -> TileElement:
        return self._tiles.get_mutable(coordinate.y, coordinate.x)

    def is_valid_coordinate(self, coordinate: Coordinate):
        return (coordinate.x in range(self._tiles.cols) and
                coordinate.y in range(self._tiles.rows))

    def swap_tile_contents(self, c1: Coordinate, c2: Coordinate):
        """
        Swaps the contents of two tiles at specified coordinate. Note that
        this does not whether tiles elements have support_tile_move set to False
        :param c1: coordinate 1
        :param c2: coordinate 2
        """
        self._tiles.swap(c1.y, c1.x, c2.y, c2.x)

    def lock_live_tiles_to_board(self):
        for pair in self._live_tiles.get_element_pairs():
            self.get_tile_at(pair.coordinate).add_game_element(pair.element)
        self._live_tiles = None

    def update(self) -> None:
        """
        update the game after a single tick has passed
        """
        self._try_apply_match_rule()
        self._try_apply_generate_rule()
        self._try_apply_move_rules()

    def _try_apply_match_rule(self):
        if self._match_rule is None or ( matches := self._match_rule.check_matches(self) ) is None:
            return
        for pair in matches.get_element_pairs():
            pass

    def _try_apply_generate_rule(self):
        if self._generator_rule is None or ( generated_tiles := self._generator_rule.produce_tiles(self) ) is None:
            return
        for pair in generated_tiles.get_element_pairs():
            self.get_tile_at(pair.coordinate).add_game_element(pair.element)

    def _try_apply_move_rules(self):
        if self._static_move_rule is not None:
            self._static_move_rule.move_tiles(self)
        if self._live_move_rule is not None:
            self._live_move_rule.move_tiles(self)

    def spawn_tiles(self):
        if self._generator_rule:
            generated_tiles = self._generator_rule.produce_tiles(self)
            if generated_tiles:
                print(f"Generated {len(generated_tiles.get_element_pairs())} tiles")
