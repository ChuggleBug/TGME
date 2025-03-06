from enum import Enum, auto
from typing import Any, Optional, Callable
from abc import ABC, abstractmethod
import tkinter as tk

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
        self._direction_fn_map: dict[DirectionButton, Callable[[DirectionButton], Any]] = {}
        self._action_fn_map: dict[ActionButton, Callable[[ActionButton], Any]] = {}

    def on_button(self, *, button: DirectionButton | ActionButton, fn: Callable[[DirectionButton | ActionButton], Any]):
        if isinstance(button, DirectionButton):
            self._direction_fn_map[button] = fn
        elif isinstance(button, ActionButton):
            self._action_fn_map[button] = fn


    @abstractmethod
    def start_controller(self):
        ...

    @abstractmethod
    def pause_controller(self):
        ...

class StateError(BaseException):
    pass


class KeyboardController(ButtonController):
    UP_KEY = "Up"
    DOWN_KEY = "Down"
    LEFT_KEY = "Left"
    RIGHT_KEY = "Right"
    PRIMARY_KEY = "space" # TODO: Why is this one work when lowercase???
    SECONDARY_KEY = "Return" # TODO: This might be different on Windows???

    def __init__(self):
        super().__init__()
        self._window: Optional[tk.Tk] = None

    def bind_to_window(self, window: tk.Tk):
        self._window = window

    def _handle_button_event(self, event: tk.Event):
        if event.keysym == KeyboardController.UP_KEY:
            self._direction_fn_map[DirectionButton.UP](DirectionButton.UP)

        elif event.keysym == KeyboardController.DOWN_KEY:
            self._direction_fn_map[DirectionButton.DOWN](DirectionButton.DOWN)

        elif event.keysym == KeyboardController.LEFT_KEY:
            self._direction_fn_map[DirectionButton.LEFT](DirectionButton.LEFT)

        elif event.keysym == KeyboardController.RIGHT_KEY:
            self._direction_fn_map[DirectionButton.RIGHT](DirectionButton.RIGHT)

        elif event.keysym == KeyboardController.PRIMARY_KEY:
            self._action_fn_map[ActionButton.PRIMARY](ActionButton.PRIMARY)

        elif event.keysym == KeyboardController.SECONDARY_KEY:
            self._action_fn_map[ActionButton.SECONDARY](ActionButton.SECONDARY)

    def pause_controller(self):
        self._window.unbind("<KeyPress>")

    def start_controller(self):
        if self._window is None:
            raise StateError("Controller was not bound to a window")

        self._window.bind("<KeyPress>", self._handle_button_event)


# create another keyboard controller for player 2 like WASD instead of up, down, left and right