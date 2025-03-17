
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Optional, Callable, Dict
from abc import ABC, abstractmethod
import tkinter as tk

class DirectionButton(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    def __str__(self):
        return self.value

    @staticmethod
    def as_set() -> frozenset[DirectionButton]:
        return frozenset([DirectionButton.UP, DirectionButton.DOWN,
                          DirectionButton.LEFT, DirectionButton.RIGHT])

class ActionButton(Enum):
    PRIMARY = 'PRIMARY'
    SECONDARY = 'SECONDARY'

    @staticmethod
    def as_set() -> frozenset[ActionButton]:
        return frozenset([ActionButton.PRIMARY, ActionButton.SECONDARY])

    def __str__(self):
        return self.value


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
    """
    Default keymaps for tkinter
    """
    UP_KEY = "Up"
    DOWN_KEY = "Down"
    LEFT_KEY = "Left"
    RIGHT_KEY = "Right"
    PRIMARY_KEY = "space"
    SECONDARY_KEY = "Return"

    def __init__(self):
        super().__init__()
        self._window: Optional[tk.Tk] = None
        self._keybinds_set: bool = False

    def export_keybind(self) -> Dict[str, str]:
        return self._keybinds

    def set_keybinds(self, keybinds: Dict[str, str]):
        self._keybinds = keybinds
        self._keybinds_set = True

    def bind_to_window(self, window: tk.Tk):
        self._window = window

    def _handle_button_event(self, event: tk.Event):
        if event.keysym == self._keybinds['UP']:
            self._direction_fn_map[DirectionButton.UP](DirectionButton.UP)

        elif event.keysym == self._keybinds['DOWN']:
            self._direction_fn_map[DirectionButton.DOWN](DirectionButton.DOWN)

        elif event.keysym == self._keybinds['LEFT']:
            self._direction_fn_map[DirectionButton.LEFT](DirectionButton.LEFT)

        elif event.keysym == self._keybinds['RIGHT']:
            self._direction_fn_map[DirectionButton.RIGHT](DirectionButton.RIGHT)

        elif event.keysym == self._keybinds['PRIMARY']:
            self._action_fn_map[ActionButton.PRIMARY](ActionButton.PRIMARY)

        elif event.keysym == self._keybinds['SECONDARY']:
            self._action_fn_map[ActionButton.SECONDARY](ActionButton.SECONDARY)

    def pause_controller(self):
        self._window.unbind("<KeyPress>")

    def start_controller(self):
        if not self._keybinds_set:
            raise StateError('Keyboard controller keybinds were not set')
        if self._window is None:
            raise StateError("Controller was not bound to a window")

        self._window.bind("<KeyPress>", self._handle_button_event)