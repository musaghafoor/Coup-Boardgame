import os

class GameUI:
    def __init__(self):
        self.game_log = []

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_title(self):
        self.clear_screen()
        print("Coup: The Dystopian Universe")
        print("=" * 30)

    def display_rules(self):
        print("\nGame Rules:")
        print("Each player starts with two coins and two influences.")
        print("On your turn, you can take one of the following actions: Income, Foreign Aid, Coup, etc.")
        print("The last player with influence left wins the game.\n")

    def display_game_state(self, players, deck):
        self.clear_screen()
        print("Current Game State:")
        print("=" * 30)
        print(f"Cards in deck: {len(deck.cards)}")
        print("\nPlayers and Status:")
        for player in players:
            card_repr = ' '.join(["[ ]" for _ in player.hand])  # Placeholder for cards
            print(f"{player.name}: {card_repr} - Coins: {player.get_coins()} - Lost Influences: {len(player.influences_lost)}")
        print("=" * 30)

    def display_message(self, message):
        print(message)

    def get_user_input(self, prompt, valid_options=None):
        while True:
            user_input = input(f"{prompt}: ").strip()
            if not valid_options or user_input in valid_options:
                return user_input
            self.display_message("Invalid input, please try again.")

    def display_menu(self, title, options):
        print(f"\n{title}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

    def update_game_log(self, message):
        self.game_log.append(message)

    def display_game_log(self):
        print("\nGame Log:")
        print("=" * 30)
        for log_entry in self.game_log:
            print(log_entry)
        print("=" * 30)

    def prompt_for_action(self, actions):
        self.display_menu("Available Actions", actions)
        index = self.get_user_input("Choose an action", [str(i) for i in range(1, len(actions) + 1)])
        return actions[int(index) - 1]

    def prompt_for_target(self, players):
        self.display_menu("Choose a target player", [player.name for player in players])
        index = self.get_user_input("Select a player", [str(i) for i in range(1, len(players) + 1)])
        return players[int(index) - 1]

    def announce_action(self, player, action, target):
        target_msg = f" on {target.name}" if target else ""
        self.display_message(f"{player.name} is attempting to perform {action.action_name}{target_msg}.")

    def prompt_for_show_card(self, player_name, card_name):
        return self.get_user_input(f"{player_name}, do you want to show the {card_name} card to win the challenge? (y/n)", ['y', 'n']) == 'y'

    def prompt_for_card_loss(self, hand, player_name):
        print(f"{player_name}, you need to lose an influence. Choose a card to lose:")
        for i, card in enumerate(hand, start=1):
            print(f"{i}. [Hidden Card]")  # Assuming the card's details are hidden

        while True:
            choice = input("Select a card number to lose: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(hand):
                return int(choice) - 1  # Return the index of the chosen card
            else:
                print("Invalid choice, please select a valid card number.")

    def show_end_game(self, winner):
        self.display_message(f"Game over! The winner is {winner.name}.")

    def prompt_play_again(self):
        return self.get_user_input("Play again? (y/n)", ['y', 'n']) == 'y'

def display_ascii_art(self):
    print(r"""
    ____ ___ _ _ ____
    / _| / _ \ | | | || _
    | | | | | || | | || |) |
    | | | | | || |_| || /
    | | | || | ___/ ||
    __| ___/ _
    _ _ ___| | ___ ___ _ __ ___ ___
    | | | |/ _ \ |/ _/ _ | ' ` _ \ / _ \
    | |/| | _/ | (| () | | | | | | /
    _/_/_||__/|| || |_|_|
    _
    | |
    ___ ___ _ _ _ | |
    / |/ _ | | | | ' \ |
    _ \ () | || | |) |
    |/_/ _,| ./
    |_|


        """)
        print("\nWelcome to Coup\n")