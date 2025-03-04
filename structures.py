import copy
from typing import TypeVar, Generic, Type

T = TypeVar('T')

class Matrix(Generic[T]):
    def __init__(self, cls: Type[T], *, rows: int, cols: int):
        """
        Constructs an instance of a matrix with the default initializer of the
        requested generic class.

        :param cls: name of class which this matrix should use
        :param rows: number of rows in matrix. Should be greater than 0
        :param cols: number of columns in matrix. Should be greater than 0
        """
        if rows <= 0:
            raise ValueError(f'rows should be greater than 0, not {rows}')
        if cols <= 0:
            raise ValueError(f'cols should be greater than 0, not {cols}')
        self._cls = cls
        self._rows = rows
        self._cols = cols
        self._board = [[cls() for _ in range(0, self._cols)] for _ in range(0, self._rows)]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def _check_bounds(self, r: int, c: int):
        if r not in range(0, self._rows):
            raise IndexError(f"r = {r} is out of range of matrix")
        if c not in range(0, self._cols):
            raise IndexError(f"c = {c} is out of range of matrix")

    def get_mutable(self, r: int, c: int) -> T:
        """
        Named 'get_mutable' to ensure the idea that this returns a reference to
        the object
        :return: mutable instance of element
        """
        self._check_bounds(r, c)
        return self._board[r][c]

    def get_copy(self, r: int, c: int) -> T:
        """
        Returns a copy which is safe to mutate, preserving the original value
        :return: copy instance of element
        """
        return copy.deepcopy(self.get_mutable(r, c))

    def set(self, r: int, c: int, value: T):
        self._check_bounds(r, c)
        self._board[r][c] = value

    # Dunders
    def __repr__(self):
        return str([f'i={i}: [{" ".join([repr(e) for e in row])}]' for i, row in enumerate(self._board)])

# Classes imported from *
__all__ = [
    Matrix.__name__
]