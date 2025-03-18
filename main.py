import tkinter as tk
from tkinter import messagebox
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

class GameSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Setup")

        tk.Label(root, text="Select Game:").pack()
        self.game_var = tk.StringVar(value="Tetris")
        tk.Radiobutton(root, text="Tetris", variable=self.game_var, value="Tetris").pack()
        tk.Radiobutton(root, text="Bejeweled", variable=self.game_var, value="Bejeweled").pack()

        tk.Label(root, text="Select Number of Players:").pack()
        self.player_var = tk.IntVar(value=1)
        tk.Radiobutton(root, text="1 Player", variable=self.player_var, value=1, command=self.toggle_player2_fields).pack()
        tk.Radiobutton(root, text="2 Players", variable=self.player_var, value=2, command=self.toggle_player2_fields).pack()

        tk.Label(root, text="Enter Board Height:").pack()
        self.height_entry = tk.Entry(root)
        self.height_entry.pack()


        tk.Label(root, text="Enter Board Width:").pack()
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


        self.player2_frame = tk.Frame(root) 

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
            self.username2_label.pack()
            self.username2_entry.pack()
            self.password2_label.pack()
            self.password2_entry.pack()
            self.login_user2_button.pack()  
            self.create_user2_button.pack()

        else:
            self.player2_frame.pack_forget()  

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
            if value >= 10:
                return value
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a number more than or equal to 10")
            return None

    def login_user(self, player_num):
        username = self.username1_entry.get().strip() if player_num == 1 else self.username2_entry.get().strip()
        password = self.password1_entry.get().strip() if player_num == 1 else self.password2_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Username and password cannot be empty.")
            return

        try:
            user = User.load_from_file(username, password=password)

            if player_num == 1:
                self.username1_label.pack_forget()
                self.username1_entry.pack_forget()
                self.password1_label.pack_forget()
                self.password1_entry.pack_forget()
                self.login_user1_button.pack_forget()
                self.create_user1_button.pack_forget()

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
            self.player1_status.pack_forget()
            self.logout_user1_button.pack_forget()

            self.username1_entry.pack()
            self.password1_entry.pack()
            self.login_user1_button.pack()
            self.create_user1_button.pack()

        else:
            self.player2_status.pack_forget()
            self.logout_user2_button.pack_forget()

            self.username2_entry.pack()
            self.password2_entry.pack()
            self.login_user2_button.pack()
            self.create_user2_button.pack()



    def start_game(self):
        game_name = self.game_var.get()
        num_players = self.player_var.get()

        height = self.get_int_input(self.height_entry)
        width = self.get_int_input(self.width_entry)

        if height is None or width is None:
            return   


        user1 = self.login_user(1)
        if num_players == 2:
            user2 = self.login_user(2)
        else:
            user2 = None 

        if not user1 or (num_players == 2 and not user2):
            return  

        game = Game()
        board1 = Board(height, width)
        PREMADE_GAMES[game_name](board1)
        game.add_board(board1)

        controller1 = KeyboardController()
        controller1.set_keybinds(user1.get_keyboard_keybinds())
        controller1.bind_to_board_window(game.get_window())

        game.bind(controller1, board_index=0)

        if num_players == 2:
            board2 = Board(height, width)
            PREMADE_GAMES[game_name](board2)
            game.add_board(board2)

            controller2 = KeyboardController()
            controller2.set_keybinds(user2.get_keyboard_keybinds())
            controller2.bind_to_board_window(game.get_window())

            game.bind(controller2, board_index=1)

        messagebox.showinfo("Game Starting", f"Starting {game_name} with {num_players} player(s)...")
        self.root.destroy()
        game.start()

if __name__ == "__main__":
    root = tk.Tk()

    window_width = 300
    window_height = 600

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    app = GameSetupApp(root)
    root.mainloop()
