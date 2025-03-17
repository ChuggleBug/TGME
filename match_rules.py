from typing import TYPE_CHECKING

from board import Board
from board_elements import Coordinate
from rules import TileMatchRule, MatchEventRule

if TYPE_CHECKING:
    from typing import Iterable, List


class MatchARowRule(TileMatchRule):

    def check_matches(self, board) -> List[Coordinate]:
        matches = []
        for y in reversed(range(board.get_height())):
            coordinate_row = [Coordinate(x, y) for x in range(board.get_width())]
            if all(map(lambda coordinate: board.get_tile_at(coordinate).has_elements(), coordinate_row)):
                matches.extend(coordinate_row)
        return matches

    def remove_matches(self, board: Board) -> List[Coordinate]:
        to_destroy = self.check_matches(board)

        for coordinate in to_destroy:
            board.get_tile_at(coordinate).apply_destroy()

        return to_destroy

class MatchNOfColorRule(TileMatchRule):

    def __init__(self, match_length: int = 3):
        self._match_length = match_length

    def set_match_length(self, match_length: int):
        self._match_length = match_length

    def check_matches(self, board) -> List[Coordinate]:
        matches = []
        for x in range(board.get_width()):
            for y in range(board.get_height()):
                for coordinate in self._check_at(board, Coordinate(x, y)):
                    if coordinate not in matches:
                        matches.append(coordinate)
        return matches

    def remove_matches(self, board: Board) -> List[Coordinate]:
        to_destroy = self.check_matches(board)

        for coordinate in to_destroy:
            board.get_tile_at(coordinate).apply_destroy()
        return to_destroy

    def _check_at(self, board: Board, coordinate: Coordinate) -> Iterable[Coordinate]:
        coordinate_set = []
        vertical_coords = [Coordinate(coordinate.x, coordinate.y + i) for i in range(self._match_length)]
        horizontal_coords = [Coordinate(coordinate.x + i, coordinate.y) for i in range(self._match_length)]
        if all(map(lambda c: board.is_valid_coordinate(c) and board.get_tile_at(c).has_colors(), vertical_coords)):
            if len(set.intersection(*[set(board.get_tile_at(c).get_colors()) for c in vertical_coords])) > 0:
                coordinate_set.extend(vertical_coords)
        if all(map(lambda c: board.is_valid_coordinate(c) and board.get_tile_at(c).has_colors(), horizontal_coords)):
            if len(set.intersection(*[set(board.get_tile_at(c).get_colors()) for c in horizontal_coords])) > 0:
                coordinate_set.extend(horizontal_coords)
        return coordinate_set


class ShiftToFillRowEventRule(MatchEventRule):

    def trigger(self, board: Board, coordinates: List[Coordinate]):
        rows: List[List[Coordinate]] = []
        for coordinate in coordinates:
            # if any row has its y coordinate, then add it to the list
            # if it does not make a new let and append it
            needs_new_row = True
            for row in rows:
                if len(row) > 0 and row[0].y == coordinate.y:
                    needs_new_row = False
                    row.append(coordinate)
                    break
            if needs_new_row:
                rows.append([coordinate])
        # remove any rows which don't have their entire row cleared
        cleared_rows = sorted([row[0].y for row in rows if len(row) == board.get_width()])
        for row in cleared_rows:
            ShiftToFillRowEventRule._shift_down_all_by_one(board, row)

    @staticmethod
    def _shift_down_all_by_one(board: Board, cleared_row: int):
        for y in reversed(range(cleared_row)):
            for x in range(board.get_width()):
                source_coordinate = Coordinate(x,y)
                target_coordinate = Coordinate(x, y + 1)
                if (not board.is_valid_coordinate(target_coordinate) or
                        board.get_tile_at(target_coordinate).has_elements() or
                        not board.get_tile_at(source_coordinate).can_support_move()):
                    continue
                board.swap_tile_contents(source_coordinate, target_coordinate)




