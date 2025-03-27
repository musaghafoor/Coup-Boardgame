# Coup Game README

This is a Python implementation of the popular  socialcard game Coup. The game supports both human and AI players, and includes various AI strategies.

## Requirements

- Python 3.6 or higher
- matplotlib library

You can install the matplotlib library using pip:

```
pip install matplotlib
```

## How to Run the Game

1. Open a terminal or command prompt and navigate to the directory containing the source code.

2. Run the `main.py` file using Python:

```
python main.py
```

4. The game will start, and you will be presented with a menu with the following options:

   1. Run game with UI
   2. Run game with AI players only
   3. Run multiple games
   4. Evaluate AI performance
   5. Quit

   Choose an option by entering the corresponding number.

5. If you choose option 1 (Run game with UI), you will be prompted to enter the number of human players (1-4) and the number of AI players (0-4). The total number of players must be between 2 and 4. For each AI player, you will be asked to select the AI type (AIPlayerMonte, AIPlayerOldMonte, AIPlayerRuleBased, or RandomAIPlayer).

6. If you choose option 2 (Run game with AI players only), you will be prompted to enter the number of AI players (2-4) and select the AI type for each player.

7. If you choose option 3 (Run multiple games), you will be prompted to enter the number of games to run, the number of AI players (2-4), and the AI type for each player. The game will run the specified number of times with the selected AI players, and display the win counts for each player.

8. If you choose option 4 (Evaluate AI performance), you will be prompted to enter the number of games to evaluate, the number of AI players (2-4), and the AI type for each player. The game will run the specified number of times with the selected AI players, and generate graphs visualizing the win percentage, average turns played, average actions played, average challenges made, and average blocks made for each AI player. The graphs will be saved in the `evaluations` folder.

9. If you choose option 5 (Quit), the program will exit.

