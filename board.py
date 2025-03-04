

from structures import Matrix

class TileElement:
    pass

class Board:
    def __init__(self, *, rows: int, cols: int):
        self._tiles = Matrix(TileElement, rows=rows, cols=cols)
        self._tiles.get_mutable(5, 6)

class Counter:
    def __init__(self):
        self._count = 0

    def count(self):
        self._count += 1

    def get_count(self):
        return self._count

