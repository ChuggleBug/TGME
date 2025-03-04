
import tkinter as tk

from abc import ABC, abstractmethod
from typing import Any, Callable
from enum import Enum, auto


class DirectionButton(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class ActionButton(Enum):
    PRIMARY = auto()
    SECONDARY = auto()

class ButtonController(ABC):
    def __init__(self):
        self._direction_fn_map: dict[DirectionButton, Callable[[], Any]] = {}
        self._button_fn_map: dict[ActionButton, Callable[[], Any]] = {}

    def on_button_press_up(self, fn: Callable[[], Any]):
        self._direction_fn_map[DirectionButton.UP] = fn

    def on_button_press_down(self, fn: Callable[[], Any]):
        self._direction_fn_map[DirectionButton.DOWN] = fn

    def on_button_press_left(self, fn: Callable[[], Any]):
        self._direction_fn_map[DirectionButton.LEFT] = fn

    def on_button_press_right(self, fn: Callable[[], Any]):
        self._direction_fn_map[DirectionButton.RIGHT] = fn

    def on_button_press_primary(self, fn: Callable[[], Any]):
        self._button_fn_map[ActionButton.PRIMARY] = fn

    def on_button_press_secondary(self, fn: Callable[[], Any]):
        self._button_fn_map[ActionButton.SECONDARY] = fn

    @abstractmethod
    def start_controller(self):
        ...

    @abstractmethod
    def pause_controller(self):
        ...


class KeyboardController(ButtonController):
    UP_KEY = "Up"
    DOWN_KEY = "Down"
    LEFT_KEY = "Left"
    RIGHT_KEY = "Right"
    PRIMARY_KEY = "Space"
    SECONDARY_KEY = "Enter"

    def _handle_button_event(self, event: tk.Event):
        if event.keysym == KeyboardController.UP_KEY:
            self._direction_fn_map[DirectionButton.UP]()
        elif event.keysym == KeyboardController.DOWN_KEY:
            self._direction_fn_map[DirectionButton.DOWN]()
        elif event.keysym == KeyboardController.LEFT_KEY:
            self._direction_fn_map[DirectionButton.LEFT]()
        elif event.keysym == KeyboardController.RIGHT_KEY:
            self._direction_fn_map[DirectionButton.RIGHT]()
        elif event.keysym == KeyboardController.PRIMARY_KEY:
            self._button_fn_map[ActionButton.PRIMARY]()
        elif event.keysym == KeyboardController.SECONDARY_KEY:
            self._button_fn_map[ActionButton.SECONDARY]()

    # TODO: Change to apply to active board
    def pause_controller(self):
        root.unbind("<KeyPress>")

    def start_controller(self):
        root.bind("<KeyPress>", self._handle_button_event)

