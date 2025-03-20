import tkinter as tk
from tkinter import messagebox
from typing import Callable

from button_controller import ActionButton, DirectionButton, KeyboardController
from examples.tetris import apply_tetris_rule
from examples.bejeweled import apply_bejeweled_rule
from board import Board
from game import Game
from user import User

PREMADE_GAMES: dict[str, Callable[[Board], None]] = {
    'Tetris': apply_tetris_rule,
    'Bejeweled': apply_bejeweled_rule
}

class GameSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Setup")

        self.logged_in_users = {}


        tk.Label(root, text="Player 1: Select Game:").pack()
        self.game_var = tk.StringVar(value="Tetris")
        tk.Radiobutton(root, text="Tetris", variable=self.game_var, value="Tetris").pack()
        tk.Radiobutton(root, text="Bejeweled", variable=self.game_var, value="Bejeweled").pack()
        self.configure_controls1_button = tk.Button(root, text="Configure Controls (P1)", command=lambda: self.configure_controls(1))
        self.configure_controls1_button.pack()

        self.player2_game_frame = tk.Frame(root)
        tk.Label(self.player2_game_frame, text="Player 2: Select Game:").pack()
        self.game_var2 = tk.StringVar(value="Tetris")
        tk.Radiobutton(self.player2_game_frame, text="Tetris", variable=self.game_var2, value="Tetris").pack()
        tk.Radiobutton(self.player2_game_frame, text="Bejeweled", variable=self.game_var2, value="Bejeweled").pack()
        self.configure_controls2_button = tk.Button(self.player2_game_frame, text="Configure Controls (P2)", command=lambda: self.configure_controls(2))


        tk.Label(root, text="Select Number of Players:").pack()
        self.player_var = tk.IntVar(value=1)
        tk.Radiobutton(root, text="1 Player", variable=self.player_var, value=1, command=self.toggle_player2_fields).pack()
        tk.Radiobutton(root, text="2 Players", variable=self.player_var, value=2, command=self.toggle_player2_fields).pack()

        #1
        self.height_q = tk.Label(root, text="Enter Board Height:")
        self.height_q.pack()
        self.height_entry = tk.Entry(root)
        self.height_entry.pack()


        self.width_q = tk.Label(root, text="Enter Board Width:")
        self.width_q.pack()
        self.width_entry = tk.Entry(root)
        self.width_entry.pack()

        self.username1_label = tk.Label(root, text="Player 1 Username:")
        self.username1_label.pack()
        self.username1_entry = tk.Entry(root)
        self.username1_entry.pack()

        self.password1_label = tk.Label(root, text="Player 1 Password:")
        self.password1_label.pack()
        self.password1_entry = tk.Entry(root, show="*")
        self.password1_entry.pack()

        
        self.login_user1_button = tk.Button(root, text="Log In", command=lambda: self.login_user(1))
        self.login_user1_button.pack()

        self.create_user1_button = tk.Button(root, text="Create User", command=lambda: self.create_user(1))
        self.create_user1_button.pack()


        #2
        self.player2_frame = tk.Frame(root) 

        self.height_q2 = tk.Label(self.player2_frame, text="Enter Board_2 Height:")
        self.height_entry2 = tk.Entry(self.player2_frame)

        self.width_q2 = tk.Label(self.player2_frame, text="Enter Board_2 Width:")
        self.width_entry2 = tk.Entry(self.player2_frame)


        self.username2_label = tk.Label(self.player2_frame, text="Player 2 Username:")
        self.username2_entry = tk.Entry(self.player2_frame)

        self.password2_label = tk.Label(self.player2_frame, text="Player 2 Password:")
        self.password2_entry = tk.Entry(self.player2_frame, show="*")

        self.login_user2_button = tk.Button(self.player2_frame, text="Log In", command=lambda: self.login_user(2))
        self.create_user2_button = tk.Button(self.player2_frame, text="Create User", command=lambda: self.create_user(2))
        self.start_button = tk.Button(
            root,
            text="Start Game",
            command=self.start_game,
            font=("Arial", 14, "bold"),
            bg="#4CAF50",  
            fg="white",
            padx=20,  
            pady=10
        )
        self.start_button.pack(pady=20, fill="x", side="bottom")


    def toggle_player2_fields(self):
        if self.player_var.get() == 2:
            self.player2_frame.pack()  
            self.height_q2.pack()
            self.height_entry2.pack()
            self.width_q2.pack() 
            self.width_entry2.pack()
            self.username2_label.pack()
            self.username2_entry.pack()
            self.password2_label.pack()
            self.password2_entry.pack()
            self.login_user2_button.pack()  
            self.create_user2_button.pack()
            self.player2_game_frame.pack()
            self.configure_controls2_button.pack()
        else:
            self.player2_frame.pack_forget()  
            self.player2_game_frame.pack_forget()


    def show_instructions(self, game_name,user1, user2, on_continue):
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title(f"{game_name} Instructions")
        instructions_window.geometry("700x550")

        instructions_text = {
            "Tetris": "TETRIS INSTRUCTIONS\n\n"
                "Objective:\n"
                "- Arrange falling blocks to form full rows.\n"
                "- Each cleared row gives 1 point.\n\n"
                "Game Over:\n"
                "- The game ends when blocks reach the top.\n\n"
                "Controls:\n"
                "- Down Button: Shift block down.\n"
                "- Left Button: Shift block left.\n"
                "- Right Button: Shift block right.\n"
                "- Primary Button: Rotate the block clockwise.\n"
                "- Secondary Button: Rotate the block counterclockwise.\n",

            "Bejeweled": "BEJEWELED INSTRUCTIONS\n\n"
                 "Objective:\n"
                 "- Swap adjacent gems to match 3 or more of the same color.\n"
                 "- Matches disappear, and new gems fall.\n\n"
                 "Game Over:\n"
                 "- No more valid moves.\n\n"
                 "Controls:\n"
                 "- Up Button: Move cursor up.\n"
                 "- Down Button: Move cursor down.\n"
                 "- Left Button: Move cursor left.\n"
                 "- Right Button: Move cursor right.\n"
                 "- Primary Button: Change to swapping state/Swap tiles.\n"
                 "- Secondary Button: Change to movement state.\n",

        }

        player1_keybinds = "\n".join([f"{action}: {key}" for action, key in user1.get_keyboard_keybinds().items()])
        player1_text = f"\nPLAYER 1 CONTROLS:\n{player1_keybinds}\n"

        if user2:
            player2_keybinds = "\n".join([f"{action}: {key}" for action, key in user2.get_keyboard_keybinds().items()])
            player2_text = f"\nPLAYER 2 CONTROLS:\n{player2_keybinds}\n"
        else:
            player2_text = ""

        label = tk.Label(instructions_window, text=instructions_text[game_name] + player1_text + player2_text, justify="left", padx=10, pady=10)
        label.pack()

        continue_button = tk.Button(instructions_window, text="Continue", command=lambda: [instructions_window.destroy(), on_continue()])
        continue_button.pack(pady=10)


    def create_user(self, player_num):
        username = self.username1_entry.get().strip() if player_num == 1 else self.username2_entry.get().strip()
        password = self.password1_entry.get().strip() if player_num == 1 else self.password2_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            User.make_new_user(username, password=password)
            messagebox.showinfo("Success", f"User '{username}' created successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create user: {e}")

    def get_int_input(self, entry):
        try:
            value = int(entry.get().strip())
            if value < 10: 
                messagebox.showerror("Input Error", "Please enter a number greater than or equal to 10")
                return None
            return value  
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input! Please enter a valid number.")
            return None

    def login_user(self, player_num):
        username = self.username1_entry.get().strip() if player_num == 1 else self.username2_entry.get().strip()
        password = self.password1_entry.get().strip() if player_num == 1 else self.password2_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Username and password cannot be empty.")
            return

        if username in self.logged_in_users:
            messagebox.showerror("Login Error", f"User '{username}' is already logged in!")
            return None
        try:
            user = User.load_from_file(username, password=password)

            self.logged_in_users[username] = user


            if player_num == 1:
                self.username1_label.pack_forget()
                self.username1_entry.pack_forget()
                self.password1_label.pack_forget()
                self.password1_entry.pack_forget()
                self.login_user1_button.pack_forget()
                self.create_user1_button.pack_forget()
                self.height_entry.pack_forget()
                self.width_entry.pack_forget()
                self.height_q.pack_forget()
                self.width_q.pack_forget()
                self.player1_status = tk.Label(self.root, text=f"Logged in as {username}", fg="green", font=("Arial", 12, "bold"))
                self.player1_status.pack()

                self.logout_user1_button = tk.Button(self.root, text="Log Out", command=lambda: self.logout_user(1))
                self.logout_user1_button.pack()

            else:
                self.username2_label.pack_forget()
                self.username2_entry.pack_forget()
                self.password2_label.pack_forget()
                self.password2_entry.pack_forget()
                self.login_user2_button.pack_forget()
                self.create_user2_button.pack_forget()
                self.height_q2.pack_forget()
                self.height_entry2.pack_forget()
                self.width_q2.pack_forget()
                self.width_entry2.pack_forget()
                self.player2_status = tk.Label(self.player2_frame, text=f"Logged in as {username}", fg="green", font=("Arial", 12, "bold"))
                self.player2_status.pack()

                self.logout_user2_button = tk.Button(self.player2_frame, text="Log Out", command=lambda: self.logout_user(2))
                self.logout_user2_button.pack()

            return user

        except ValueError:
            messagebox.showerror("Login Error", "Invalid username or password. Try again or create a new user.")
        except FileNotFoundError:
            if messagebox.askyesno("Create User?", f'User \"{username}\" does not exist. Create a new account?'):
                self.create_user(player_num)


    def logout_user(self, player_num):
        if player_num == 1:
            username = self.player1_status.cget("text").replace("Logged in as ", "")
            self.player1_status.pack_forget()
            self.logout_user1_button.pack_forget()
            self.logged_in_users.pop(username, None)

            self.height_q.pack()
            self.height_entry.pack()

            self.width_q.pack()
            self.width_entry.pack()

            self.player1_status.pack_forget()

            self.username1_label.pack()
            self.username1_entry.pack()

            self.password1_label.pack()
            self.password1_entry.pack()

            self.login_user1_button.pack()
            self.create_user1_button.pack()

        else:
            username = self.player2_status.cget("text").replace("Logged in as ", "")
            self.player2_status.pack_forget()
            self.logout_user2_button.pack_forget()
            self.logged_in_users.pop(username, None)

            self.height_q2.pack()
            self.height_entry2.pack()
            self.width_q2.pack()
            self.width_entry2.pack()

            self.username2_label.pack()
            self.username2_entry.pack()

            self.password2_label.pack()
            self.password2_entry.pack()

            self.login_user2_button.pack()
            self.create_user2_button.pack()

    def configure_controls(self, player_num):
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Configure Controls - Player {player_num}")

        if player_num == 1:  
            current_user = self.logged_in_users.get(self.username1_entry.get().strip()) 
        else:
            current_user = self.logged_in_users.get(self.username2_entry.get().strip())

        if not current_user:
            messagebox.showerror("Error", "User must be logged in to configure controls.")
            config_window.destroy()
            return

        control_vars = {str(button): tk.StringVar(value=current_user.get_keyboard_keybinds().get(str(button), "Press a key"))
                        for button in (DirectionButton.UP, DirectionButton.DOWN, DirectionButton.LEFT,DirectionButton.RIGHT,
                                    ActionButton.PRIMARY, ActionButton.SECONDARY)}

        def set_key(button):
            def on_key_press(event):
                control_vars[str(button)].set(event.keysym)
                key_buttons[button].config(text=f"{button}: {event.keysym}")
                config_window.unbind("<Key>")

            config_window.bind("<Key>", on_key_press)

        key_buttons = {}

        for i, button in enumerate(control_vars.keys()):
            tk.Label(config_window, text=button).grid(row=i, column=0, padx=10, pady=5)
            key_buttons[button] = tk.Button(config_window, text=control_vars[button].get(), 
                                            command=lambda b=button: set_key(b))
            key_buttons[button].grid(row=i, column=1, padx=10, pady=5)

        def save_controls():
            for button, var in control_vars.items():
                if button in [str(b) for b in DirectionButton.as_set()]:
                    current_user.set_keyboard_keybind(DirectionButton[button], var.get())
                elif button in [str(b) for b in ActionButton.as_set()]:
                    current_user.set_keyboard_keybind(ActionButton[button], var.get())

            current_user.save_user(password=self.password1_entry.get().strip() if player_num == 1 else 
                                                self.password2_entry.get().strip())

            messagebox.showinfo("Success", f"Controls saved for {current_user._username}!")
            config_window.destroy()

        save_button = tk.Button(config_window, text="Save Controls", command=save_controls)
        save_button.grid(row=len(control_vars), column=0, columnspan=2, pady=10)


    def start_game(self):
        num_players = self.player_var.get()

        game_name1 = self.game_var.get()
        game_name2 = self.game_var2.get() if num_players == 2 else game_name1

        height = self.get_int_input(self.height_entry)
        width = self.get_int_input(self.width_entry)
        height2 = self.get_int_input(self.height_entry2) if num_players == 2 else None
        width2 = self.get_int_input(self.width_entry2) if num_players == 2 else None


        if height is None or width is None or (num_players == 2 and (height2 is None or width2 is None)):
            return 

        logged_in_users_list = list(self.logged_in_users.values())
        user1 = logged_in_users_list[0] if len(logged_in_users_list) > 0 else None
        user2 = logged_in_users_list[1] if num_players == 2 and len(logged_in_users_list) > 1 else None


        if not user1 or (num_players == 2 and not user2):
            messagebox.showerror("Error", "Both players must be logged in before starting the game.")
            return  

        def start_after_instructions():
            game = Game()
            board1 = Board(height, width)
            PREMADE_GAMES[game_name1](board1)
            game.add_board(board1)

            controller1 = KeyboardController()
            controller1.set_keybinds(user1.get_keyboard_keybinds())
            controller1.bind_to_board_window(game.get_window())
            game.bind(controller1, board_index=0)

            if num_players == 2:
                board2 = Board(height2, width2)
                PREMADE_GAMES[game_name2](board2)
                game.add_board(board2)

                controller2 = KeyboardController()
                controller2.set_keybinds(user2.get_keyboard_keybinds())
                controller2.bind_to_board_window(game.get_window())

                game.bind(controller2, board_index=1)

            self.root.destroy()
            game.start()
        
        self.show_instructions(game_name1, user1, user2, start_after_instructions)


if __name__ == "__main__":
    root = tk.Tk()

    window_width = 600
    window_height = 800

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    app = GameSetupApp(root)
    root.mainloop()


