
from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Union

from pathlib import Path
import json
import copy

from button_controller import DirectionButton, ActionButton, DEFAULT_KEYBOARD_KEYBINDS

if TYPE_CHECKING:
    from typing import Any

_USER_BASE_PATH = Path('./user')

_BASE_USER_DICT = {
    'username': '',
    'password': '',
    'keyboard keybinds': {}
}


def _get_user_file(username: str):
    return _USER_BASE_PATH / f'{username}.json'

def _generate_hash(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()

class User:
    # Annotations for convenience
    _username: str
    _keyboard_keybinds: dict[str, str]

    @classmethod
    def load_from_file(cls, username: str, *, password: str) -> User:
        user = User()
        with open(_get_user_file(username), mode='r', encoding='utf-8') as fp:
            user_dict: dict[str, Any] = json.load(fp)
            if _generate_hash(password) != user_dict['password']:
                raise ValueError(f'password for {username} does not match')
            user._username = username
            user._keyboard_keybinds = user_dict.get('keyboard keybinds', {})
        return user

    @classmethod
    def make_new_user(cls, username: str, *, password: str) -> User:
        if _get_user_file(username).exists():
            raise FileExistsError(f'user {username} already exists')
        user = User()
        user._username = username
        user._keyboard_keybinds = {}
        user_dict = user._as_dict()
        user_dict['password'] = _generate_hash(password)
        user_dict['keyboard keybinds'] = copy.deepcopy(DEFAULT_KEYBOARD_KEYBINDS)
        with open(_get_user_file(username), mode='w+', encoding='utf-8') as fp:
            json.dump(user_dict, fp)
        return user

    def set_keyboard_keybind(self, button: Union[DirectionButton, ActionButton], keybind: str):
        if button not in DirectionButton.as_set() | ActionButton.as_set():
            raise ValueError(f'Invalid button assignment. {button} not in {list(DirectionButton.as_set() | ActionButton.as_set())}')
        self._keyboard_keybinds[str(button)] = keybind

    def save_user(self, *, password: str):
        # load the file and check if the password matches, if so, then overwrite
        with open(_get_user_file(self._username), mode='r', encoding='utf-8') as fp:
            if _generate_hash(password) != json.load(fp)['password']:
                raise ValueError(f'password for {self._username} does not match')
        user_dict = self._as_dict()
        user_dict['password'] = _generate_hash(password)
        with open(_get_user_file(self._username), mode='w+', encoding='utf-8') as fp:
            json.dump(user_dict, fp)

    def get_keyboard_keybinds(self) -> dict[str, str]:
        return self._keyboard_keybinds

    def _as_dict(self) -> dict[str, Any]:
        """
        Generates a dictionary of the user. Does not include the password
        """
        user_dict = copy.deepcopy(_BASE_USER_DICT)
        user_dict['username'] = self._username
        user_dict['keyboard keybinds'] = self._keyboard_keybinds
        return user_dict


if __name__ == '__main__':
    # Ideally the password would not be saved in plaintext in code
    # and would be saved as secret or environment variable
    # For this project, this does not matter
    if not _get_user_file('test_user1').exists():
        User.make_new_user('test_user1', password='test_user1')
    if not _get_user_file('test_user2').exists():
        User.make_new_user('test_user2', password='test_user2')
    test_user1 = User.load_from_file('test_user1', password='test_user1')
    test_user2 = User.load_from_file('test_user2', password='test_user2')

    # sets default keybinds
    test_user1.set_keyboard_keybind(DirectionButton.UP, 'w')
    test_user1.set_keyboard_keybind(DirectionButton.DOWN, 's')
    test_user1.set_keyboard_keybind(DirectionButton.LEFT, 'a')
    test_user1.set_keyboard_keybind(DirectionButton.RIGHT, 'd')
    # I have no idea what these should be
    test_user1.set_keyboard_keybind(ActionButton.PRIMARY, 'e')
    test_user1.set_keyboard_keybind(ActionButton.SECONDARY, 'q')

    # sets default keybinds
    test_user2.set_keyboard_keybind(DirectionButton.UP, 'Up')
    test_user2.set_keyboard_keybind(DirectionButton.DOWN, 'Down')
    test_user2.set_keyboard_keybind(DirectionButton.LEFT, 'Left')
    test_user2.set_keyboard_keybind(DirectionButton.RIGHT, 'Right')
    # I have no idea what these should be
    test_user2.set_keyboard_keybind(ActionButton.PRIMARY, 'space')
    test_user2.set_keyboard_keybind(ActionButton.SECONDARY, 'Return')

    # Save users
    test_user1.save_user(password='test_user1')
    test_user2.save_user(password='test_user2')


