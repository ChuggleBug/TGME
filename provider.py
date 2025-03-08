from __future__ import annotations
from typing import TYPE_CHECKING

import copy
import random

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from board_elements import ElementSet

if TYPE_CHECKING:
    from typing import List, Tuple


T = TypeVar("T", bound=ElementSet)


class ElementProvider(ABC, Generic[T]):
    @abstractmethod
    def provide(self) -> T:
        """
        Returns an instance of T.

        It is up to the implementing class as how to return a value
        :return: Any object of type T
        """
        ...

class UniformRandomElementProvider(ElementProvider, Generic[T]):

    def __init__(self):
        self._elementChoices: List[T] = []

    def add_choice(self, option: T):
        """
        Each option will have the same chance of happening
        :param option:
        """
        self._elementChoices.append(option)

    def provide(self) -> T:
        if len(self._elementChoices) == 0:
            raise ValueError("Provider has no elements to provide")
        return copy.deepcopy(random.choice(self._elementChoices))


class WeightedRandomElementProvider(ElementProvider, Generic[T]):

    def __init__(self):
        self._elementChoices: List[Tuple[T, int]] = []

    def add_choice(self, *, option: T, weight: int):
        """
        Add a potential element which can be chosen from at random.
        Weight values should be a number from 0 to 100 representing the
        percen chance of it occurring
        :param option: Element which can be chosen
        :param weight: Percent chance of it occurring as an integer
        """
        if weight < 0 or weight > 100:
            raise ValueError(f"weight={weight} not in range [0-100]")
        if sum(map(lambda t: t[1], self._elementChoices), start=weight) > 100:
            raise ValueError("Percent of element chances exceeds 100")
        self._elementChoices.append((option, weight))

    def _generate_random(self) -> T:
        options, weights = zip(*self._elementChoices)  # Unpack elements and weights
        return copy.deepcopy(random.choices(options, weights=weights)[0])

    def provide(self) -> T:
        if sum(map(lambda t: t[1], self._elementChoices)) != 100:
            raise ValueError("Sum of weights is not equal to 100")
        return self._generate_random()

class RandomRepeatingQueueElementProvider(ElementProvider, Generic[T]):

    def __init__(self):
        self._element_choices: List[T] = []
        self._queue: List[T] = []

    def add_choice(self, option: T):
        self._element_choices.append(option)
        self._queue = self._element_choices[:]
        random.shuffle(self._queue)

    def _reshuffle(self):
        if self._element_choices:
            self._queue = self._element_choices[:]
            random.shuffle(self._queue)

    def provide(self) -> T:
        if not self._element_choices:
            raise ValueError("Provider has no elements to provide")

        if not self._queue:
            self._reshuffle()

        return copy.deepcopy(self._queue.pop())
