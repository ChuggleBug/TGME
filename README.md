# Tile-Matching Game Engine
## Usage Guide
There are currently two default game available:
- Tetris
- Bejeweled

These two games can be played using the provided GUI in `main.py`

## Controls
There are 6 main controller buttons available:
- 4 Directional Buttons
- A Primary Button
- A Secondary Button

The actual keyboard inputs associated can be seen under a 
user's account section
## Account information
Simple username and password authentication can be accessed using the GUI. 
Accounts allow players to change their preset keyboard bindings when 
playing a game. These accounts can be seen in `TMGE/user/{username}.json`

Two default user accounts have been provided credentials are
- username: `test_user1`, password: `test_user1`
- username: `test_user2`, password: `test_user2`

## Additional Notes
The GUI was developed with Windows in mind. Because of the way that 
tkiner works, there might be some slight visual issues when using operating
systems. The core functionality is not affected, however. 

## Python Information
Most of the development was done under python3.12. Older versions of
python might work, but have not been tested to ensure quality
