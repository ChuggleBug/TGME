from __future__ import annotations
from typing import TYPE_CHECKING

from constants import Color
from game import Game
from structures import Matrix
from rules import UserInputRuleSet, GravityRule, MatchEventRule, GameOverException
from board_elements import Coordinate
from constants import TK_COLOR_MAP

if TYPE_CHECKING:
    from typing import List, Set, Optional, Iterable
    from button_controller import DirectionButton, ActionButton
    from board_elements import GameElement, ElementSet, BoardElementSet
    from shift_rules import ShiftDirection
    from rules import TileMatchRule, TileGeneratorRule, TileMovementRule, UserInputRule, GameConditionRule


class Cursor:
    def __init__(self):
        self._primary_location: Coordinate = Coordinate(0, 0)
        self._secondary_location: Optional[Coordinate] = None
        self._is_in_swapping_state: bool = False

    def set_primary_position(self, coordinate: Coordinate):
        self._primary_location = coordinate

    def set_secondary_position(self, coordinate: Coordinate):
        self._secondary_location = coordinate

    def get_primary_position(self) -> Coordinate:
        return self._primary_location

    def has_secondary_position(self) -> bool:
        return self._secondary_location is not None

    def get_secondary_position(self) -> Coordinate:
        return self._secondary_location

    def is_in_movement_state(self) -> bool:
        return not self._is_in_swapping_state

    def is_in_swapping_state(self) -> bool:
        return self._is_in_swapping_state

    def set_movement_state(self):
        self._is_in_swapping_state = False
        self._secondary_location = None

    def set_swapping_state(self):
        self._is_in_swapping_state = True

    def draw(self, canvas, cell_height, cell_width):
        pp = self.get_primary_position()
        x1, y1 = pp.x * cell_width, pp.y * cell_height
        x2, y2 = x1 + cell_width, y1 + cell_height

        if self.is_in_movement_state():
            canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3, fill="")

        if self.is_in_swapping_state():
            # Primary X
            canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3, fill="")

            if self.has_secondary_position():
                sp = self.get_secondary_position()
                w1, u1 = sp.x * cell_width, sp.y * cell_height
                w2, u2 = w1 + cell_width, u1 + cell_height

                #Secondary X
                corner_length = 15
                canvas.create_line(w1, u1, w1 + corner_length, u1, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w1, u1, w1, u1 + corner_length, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w2, u1, w2 - corner_length, u1, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w2, u1, w2, u1 + corner_length, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w1, u2, w1 + corner_length, u2, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w1, u2, w1, u2 - corner_length, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w2, u2, w2 - corner_length, u2, fill=TK_COLOR_MAP[Color.GRAY], width=3)
                canvas.create_line(w2, u2, w2, u2 - corner_length, fill=TK_COLOR_MAP[Color.GRAY], width=3)



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
        return all(map(lambda e: e.supports_move_through, self._elements))

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

    def apply_destroy(self):
        """
        Applies a destroy effect to this tile set.
        If any game element has do_block_destroy, then only the game element is destroyed
        """
        # check if any element blocks a destroy
        for element in self._elements:
            if element.do_block_destroy:
                self._elements.remove(element)
                return
        # clear the tile element set
        self._elements = []

    def has_colors(self):
        return any(map(lambda element: element.supports_color, self._elements))

    def get_colors(self) -> List[Color]:
        return [element.element_color for element in self._elements if element.supports_color]


class Board:
    def __init__(self, height: int, width: int):
        self._tiles: Matrix[TileElement] = Matrix(rows=height, cols=width, initializer=lambda: TileElement())
        self._match_rule: Optional[TileMatchRule] = None
        self._generator_rule: Optional[TileGeneratorRule] = None
        self._live_tiles: Optional[ElementSet] = None
        self._input_rules: List[UserInputRuleSet] = []
        self._static_move_rule: Optional[TileMovementRule] = None
        self._match_events: List[MatchEventRule] = []
        self._gravity_rule: Optional[GravityRule] = None
        self._game_condition: List[GameConditionRule] = []
        self._cursor: Optional[Cursor] = None
        self._is_game_over: bool = False
        self._game = None 
    
    def set_game(self, game: Game):
        """Set the reference to the Game instance."""
        self._game = game

    def is_game_over(self) -> bool:
       return self._is_game_over

    def get_live_tiles(self) -> Optional[BoardElementSet]:
        return self._live_tiles

    def set_live_tile(self, live_tiles: Optional[BoardElementSet]):
        self._live_tiles = live_tiles

    def has_live_tiles(self) -> bool:
        return self._live_tiles is not None

    def enable_cursor(self):
        self._cursor = Cursor()

    def has_cursor(self) -> bool:
        return self._cursor is not None

    def get_cursor(self) -> Cursor:
        return self._cursor

    def set_tile_match_rule(self, match_rule: TileMatchRule):
        self._match_rule = match_rule

    def get_tile_match_rule(self) -> TileMatchRule:
        return self._match_rule

    def set_tile_generator_rule(self, generator_rule: TileGeneratorRule):
        self._generator_rule = generator_rule

    def add_user_input_rule(self, input_rule: UserInputRule, *, input_set: Set[DirectionButton | ActionButton]):
        self._input_rules.append(UserInputRuleSet(input_rule, input_set))

    def set_static_tile_move_rule(self, move_rule: TileMovementRule):
        self._static_move_rule = move_rule

    def get_static_tile_move_direction(self) -> Optional[ShiftDirection]:
        return self._static_move_rule.get_shift_direction() if self._static_move_rule is not None else None

    def set_gravity_rule(self, gravity_rule: GravityRule):
        self._gravity_rule = gravity_rule

    def add_match_event_rule(self, match_event: MatchEventRule):
        self._match_events.append(match_event)

    def add_game_condition_rule(self, game_condition: GameConditionRule):
        self._game_condition.append(game_condition)

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

    def update(self, time_ms: int) -> None:
        """
        update the game after a single tick has passed
        """
        if not self._is_game_over:
            try:
                self._try_apply_match_rule()
                self._try_apply_generate_rule()
                self._try_apply_move_rules()
                self._try_apply_gravity_rule(time_ms)
                self._try_apply_game_condition_rule()
            except GameOverException:
                self._is_game_over = True
                self._cursor = None

    def _try_apply_match_rule(self):
        if self._match_rule is None:
            return
        destroyed_tiles = self._match_rule.remove_matches(self)
        if len(destroyed_tiles) > 0:
            if self._game:
                self._game.update_score(self,1)
            for event in self._match_events:
                event.trigger(self, destroyed_tiles)

    def _try_apply_generate_rule(self):
        if self._generator_rule is None or ( generated_tiles := self._generator_rule.produce_tiles(self) ) is None:
            return
        for pair in generated_tiles.get_element_pairs():
            self.get_tile_at(pair.coordinate).add_game_element(pair.element)

    def _try_apply_move_rules(self):
        if self._static_move_rule is not None:
            self._static_move_rule.move_tiles(self)

    def _try_apply_gravity_rule(self, time_ms: int):
        if self._gravity_rule is not None:
            self._gravity_rule.update(self, current_time=time_ms)

    def _try_apply_game_condition_rule(self):
        for condition in self._game_condition:
            condition.check_game_condition(self)
