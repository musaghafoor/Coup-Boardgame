import random
import os
from game.game import Game
from players.player import Player
from players.ai_player import *
from cards.deck import Deck
import matplotlib.pyplot as plt

def setup_game():
    deck = Deck()
    game = Game(deck)
    num_players = int(input("Enter the number of human players (1-4): "))

    if num_players < 1 or num_players > 4:
        print("Invalid number of human players. Please choose between 1 and 4.")
        return None

    for i in range(num_players):
        player = Player(f"Player {i+1}")
        game.players.append(player)

    num_ai_players = int(input(f"Enter the number of AI players (0-{4 - num_players}): "))

    if num_ai_players < 0 or num_ai_players > 4 - num_players:
        print(f"Invalid number of AI players. Please choose between 0 and {4 - num_players}.")
        return None

    for i in range(num_ai_players):
        ai_type = input(f"Select AI type for AI Player {i+1} (1 - AIPlayerMonte, 2 - AIPlayerOldMonte, 3 - AIPlayerRuleBased, 4 - RandomAIPlayer): ")
        if ai_type == "1":
            player = AIPlayerMonte(f"AI Player {i+1}")
        elif ai_type == "2":
            player = AIPlayerOldMonte(f"AI Player {i+1}")
        elif ai_type == "3":
            player = AIPlayerRuleBased(f"AI Player {i+1}")
        else:
            player = RandomAIPlayer(f"AI Player {i+1}")
        game.players.append(player)

    game.setup()

    for player in game.players:
        if isinstance(player, AIPlayerMonte) or isinstance(player, AIPlayerOldMonte) or isinstance(player, AIPlayerRuleBased) or isinstance(player, RandomAIPlayer):
            player.game = game
            player.setup()

    return game


def setup_ai_game(num_players, ai_types):
    deck = Deck()
    game = Game(deck)
    ai_players = []
    for i in range(num_players):
        if ai_types[i] == "1":
            player = AIPlayerMonte(f"AI Player Monte Carlo {i+1}")
        elif ai_types[i] == "2":
            player = AIPlayerOldMonte(f"Old Monte AI Player {i+1}")
        elif ai_types[i] == "3":
            player = AIPlayerRuleBased(f"Rule based AI Playe {i+1}")
        else:
            player = RandomAIPlayer(f"Random AI Player {i+1}")
        player.game = game
        ai_players.append(player)
    game.players = ai_players
    game.setup()
    return game

def run_multiple_games():
    num_games = int(input("Enter the number of games to run: "))
    num_players = int(input("Enter the number of AI players (2-4): "))
    ai_types = []
    for i in range(num_players):
        ai_type = input(f"Select AI type for AI Player {i+1} (1 - AIPlayerMonte, 2 - AIPlayerOldMonte, 3 - AIPlayerRuleBased, 4 - RandomAIPlayer): ")
        ai_types.append(ai_type)
    win_counts = {}
    for i in range(num_games):
        print(f"\nGame {i+1}")
        game = setup_ai_game(num_players, ai_types)
        game.play_game()

        remaining_players = game.players_remaining()
        if remaining_players:
            winner = remaining_players[0]
            win_counts[winner.name] = win_counts.get(winner.name, 0) + 1
        else:
            print("No winner for this game.")
    print("\nWin Counts:")
    for player, wins in win_counts.items():
        print(f"{player}: {wins} wins")

def evaluate_ai_performance():
    num_games = int(input("Enter the number of games to evaluate: "))
    num_players = int(input("Enter the number of AI players (2-4): "))
    ai_types = []
    for i in range(num_players):
        ai_type = input(f"Select AI type for AI Player {i+1} (1 - AIPlayerMonte, 2 - AIPlayerOldMonte, 3 - AIPlayerRuleBased, 4 - RandomAIPlayer): ")
        ai_types.append(ai_type)
    
    win_counts = {}
    total_turns = {}
    total_actions = {}
    total_challenges = {}
    total_blocks = {}
    
    for i in range(num_games):
        print(f"\nEvaluating Game {i+1}")
        game = setup_ai_game(num_players, ai_types)
        game.play_game()
        remaining_players = game.players_remaining()
        if remaining_players:
            winner = remaining_players[0]
            win_counts[winner.name] = win_counts.get(winner.name, 0) + 1
        else:
            print("No winner for this game.")
        
        for player in game.players:
            total_turns[player.name] = total_turns.get(player.name, 0) + player.turns_played
            total_actions[player.name] = total_actions.get(player.name, 0) + player.actions_played
            total_challenges[player.name] = total_challenges.get(player.name, 0) + player.challenges_made
            total_blocks[player.name] = total_blocks.get(player.name, 0) + player.blocks_made
    
    print("\nEvaluation Results:")
    print("Win Counts:")
    for player, wins in win_counts.items():
        print(f"{player}: {wins} wins")
    
    print("\nAverage Turns Played:")
    for player, turns in total_turns.items():
        avg_turns = turns / num_games
        print(f"{player}: {avg_turns:.2f} turns")
    
    print("\nAverage Actions Played:")
    for player, actions in total_actions.items():
        avg_actions = actions / num_games
        print(f"{player}: {avg_actions:.2f} actions")
    
    print("\nAverage Challenges Made:")
    for player, challenges in total_challenges.items():
        avg_challenges = challenges / num_games
        print(f"{player}: {avg_challenges:.2f} challenges")
    
    print("\nAverage Blocks Made:")
    for player, blocks in total_blocks.items():
        avg_blocks = blocks / num_games
        print(f"{player}: {avg_blocks:.2f} blocks")
    
    # Create a folder for evaluations if it doesn't exist
    evaluations_folder = "evaluations"
    if not os.path.exists(evaluations_folder):
        os.makedirs(evaluations_folder)
    
    # Generate win percentage graph and save it to evaluations folder
    plt.figure(figsize=(14, 8))  # Increase figure size
    plt.bar(win_counts.keys(), [count / num_games * 100 for count in win_counts.values()])
    plt.xlabel("AI Player")
    plt.ylabel("Win Percentage")
    plt.title("Win Percentage of AI Players")
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align them to the right
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    win_percentage_file = os.path.join(evaluations_folder, "win_percentage.png")
    plt.savefig(win_percentage_file)
    plt.close()
    
    # Generate average turns played graph and save it to evaluations folder
    plt.figure(figsize=(14, 8))  # Increase figure size
    plt.bar(total_turns.keys(), [turns / num_games for turns in total_turns.values()])
    plt.xlabel("AI Player")
    plt.ylabel("Average Turns Played")
    plt.title("Average Turns Played by AI Players")
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align them to the right
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    avg_turns_file = os.path.join(evaluations_folder, "average_turns_played.png")
    plt.savefig(avg_turns_file)
    plt.close()
    
    # Generate average actions played graph and save it to evaluations folder
    plt.figure(figsize=(14, 8))  # Increase figure size
    plt.bar(total_actions.keys(), [actions / num_games for actions in total_actions.values()])
    plt.xlabel("AI Player")
    plt.ylabel("Average Actions Played")
    plt.title("Average Actions Played by AI Players")
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align them to the right
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    avg_actions_file = os.path.join(evaluations_folder, "average_actions_played.png")
    plt.savefig(avg_actions_file)
    plt.close()
    
    # Generate average challenges made graph and save it to evaluations folder
    plt.figure(figsize=(14, 8))  # Increase figure size
    plt.bar(total_challenges.keys(), [challenges / num_games for challenges in total_challenges.values()])
    plt.xlabel("AI Player")
    plt.ylabel("Average Challenges Made")
    plt.title("Average Challenges Made by AI Players")
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align them to the right
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    avg_challenges_file = os.path.join(evaluations_folder, "average_challenges_made.png")
    plt.savefig(avg_challenges_file)
    plt.close()
    
    # Generate average blocks made graph and save it to evaluations folder
    plt.figure(figsize=(14, 8))  # Increase figure size
    plt.bar(total_blocks.keys(), [blocks / num_games for blocks in total_blocks.values()])
    plt.xlabel("AI Player")
    plt.ylabel("Average Blocks Made")
    plt.title("Average Blocks Made by AI Players")
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align them to the right
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    avg_blocks_file = os.path.join(evaluations_folder, "average_blocks_made.png")
    plt.savefig(avg_blocks_file)
    plt.close()
    
def main():
    while True:
        print("\nMenu:")
        print("1. Run game with UI")
        print("2. Run game with AI players only")
        print("3. Run multiple games")
        print("4. Evaluate AI performance")
        print("5. Quit")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            game = setup_game()
            game.play_game()
        elif choice == "2":
            num_players = int(input("Enter the number of AI players (2-4): "))
            ai_types = []
            for i in range(num_players):
                ai_type = input(f"Select AI type for AI Player {i+1} (1 - AIPlayerMonte, 2 - AIPlayerOldMonte, 3 - AIPlayerRuleBased, 4 - RandomAIPlayer): ")
                ai_types.append(ai_type)
            game = setup_ai_game(num_players, ai_types)
            game.play_game()
        elif choice == "3":
            run_multiple_games()
        elif choice == "4":
            evaluate_ai_performance()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()