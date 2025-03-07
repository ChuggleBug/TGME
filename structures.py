import copy
from typing import TypeVar, Generic, Type, Callable

T = TypeVar('T')


class Matrix(Generic[T]):
    """
    Representation of a 2D array in the form of a matrix

    Note:
        The matrix is initialized using a callable initializer function, allowing for greater
        flexibility in object creation. This avoids limitations related to requiring a default
        constructor for the generic type.
    """

    def __init__(self, *, rows: int, cols: int, initializer: Callable[[], T]):
        """
        Constructs an instance of a matrix with elements initialized by the provided initializer function.

        :param initializer: A callable that returns an instance of the desired type when invoked.
        :param rows: Number of rows in the matrix. Should be greater than 0.
        :param cols: Number of columns in the matrix. Should be greater than 0.
        """
        if rows <= 0:
            raise ValueError(f'rows should be greater than 0, not {rows}')
        if cols <= 0:
            raise ValueError(f'cols should be greater than 0, not {cols}')

        self._rows = rows
        self._cols = cols
        self._entry = [[initializer() for _ in range(self._cols)] for _ in range(self._rows)]

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
        return self._entry[r][c]

    def get_copy(self, r: int, c: int) -> T:
        """
        Returns a copy which is safe to mutate, preserving the original value
        :return: copy instance of element
        """
        return copy.deepcopy(self.get_mutable(r, c))

    def set(self, r: int, c: int, value: T):
        self._check_bounds(r, c)
        self._entry[r][c] = value

    def swap(self, r1: int, c1: int, r2: int, c2: int):
        self._check_bounds(r1, c1)
        self._check_bounds(r2, c2)
        self._entry[r1][c1], self._entry[r2][c2] = self._entry[r2][c2], self._entry[r1][c1]

    # Dunders
    def __repr__(self):
        return str([f'i={i}: [{" ".join([repr(e) for e in row])}]' for i, row in enumerate(self._entry)])


# Classes imported from *
__all__ = [
    Matrix.__name__
]
