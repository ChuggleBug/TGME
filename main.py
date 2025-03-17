
import sys
import re
from typing import Callable

from button_controller import KeyboardController
from examples.tetris import apply_tetris_rule
from examples.bejeweled import apply_bejeweled_rule
from board import Board
from game import Game
from user import User

PREMADE_GAMES: dict[str, Callable[[Board], None]] = {
    'Tetris': apply_tetris_rule,
    'Bejeweled': apply_bejeweled_rule
}

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def login_or_create_user() -> User:
    while True:
        username = input('Enter username: ').strip()
        password = input(f'Enter {username}\'s password: ').strip()

        try:
            user = User.load_from_file(username, password=password)
            print(f'\nWelcome back, {username}!\n')
            return user  # Successfully logged in, exit the loop
        except ValueError:
            print('Invalid username or password. Please try again.\n')
            continue  # Re-prompt for username and password
        except FileNotFoundError:
            print(f'User "{username}" does not exist.')

            # Regex patterns for "yes" and "no" inputs
            yes_pattern = re.compile(r'^\s*(y|yes)\s*$', re.IGNORECASE)
            no_pattern = re.compile(r'^\s*(n|no)\s*$', re.IGNORECASE)

            new_user_input = input(f'Would you like to create a new user "{username}"? (y/n): ').strip()

            if yes_pattern.match(new_user_input):  # User agrees to create an account
                new_user_password = input(f'Enter password for new user "{username}": ').strip()
                new_user = User.make_new_user(username, password=new_user_password)
                print(f'\nUser "{username}" created successfully!\n')

                print('Before continuing, please go to user configuration and set keybinds.\n')

                print("Goodbye")
                sys.exit(0)
            else:  # Any input that isn't explicitly "yes" will be treated as "no"
                print("\nReturning to account selection...\n")
        return User.load_from_file(username, password=password)


def main():
    print('Welcome to the TGME.')
    print('There are currently two games:')
    print('\t- Tetris')
    print('\t- Bejeweled')
    print()

    # Prompt user for game selection
    game_name = input('Which one would you like to play: ').strip()
    while game_name not in PREMADE_GAMES:
        print(f"'{game_name}' is not a valid game. Try again.")
        game_name = input('Which one would you like to play: ').strip()

    # Get board dimensions
    height = get_int_input('Enter board height: ')
    width = get_int_input('Enter board width: ')

    user = login_or_create_user()

    # Setup the game
    game = Game()
    board = Board(height, width)

    controller = KeyboardController()
    controller.set_keybinds(user.get_keyboard_keybinds())

    # Call the corresponding apply_*_rule
    PREMADE_GAMES[game_name](board)

    game.bind(controller, board)
    controller.bind_to_window(game.get_window())

    # Game configurations
    print(f"\nGame Selected: {game_name}")
    print(f"Board Size: height={height} x width={width}")
    print()
    print(f'Starting {game_name}...')
    game.start()

if __name__ == '__main__':
    main()
