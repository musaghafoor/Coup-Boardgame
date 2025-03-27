"""
This module defines the player class. It handles all the methods and actions related to the players.
"""

from exceptions.game_exceptions import *
from actions.action import Income, ForeignAid, Coup, Tax, Assassinate, Steal, Exchange

class Player:
    def __init__(self, name):
        self.name = name
        self.game = None
        self.reset()
        self.turns_played = 0
        self.actions_played = 0
        self.challenges_made = 0
        self.blocks_made = 0

    def reset(self):
        """Resets the player variables"""
        self.hand = []
        self.coins = 2
        self._is_eliminated = False
        self.influences_lost = []
        self.turns_played = 0
        self.actions_played = 0
        self.challenges_made = 0
        self.blocks_made = 0

    def is_human(self):
        """A method to check if the player is a human or an AIPlayer"""
        return True

    def prompt_challenge(self, action):
        """Prompts the player for challenging"""
        print(f"\n{self.name}, do you want to challenge the action {action.action_name}? (y/n)")
        while True:
            choice = input("Enter your choice: ").lower().strip()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def prompt_block(self, action):
        """Prompts the player for blocking, showing the required blocking cards"""
        if action.action_name == "Foreign Aid":
            print(f"\n{self.name}, {action.player.name} is attempting Foreign Aid. Do you want to block by claiming Duke? (y/n)")
            while True:
                choice = input("Enter your choice: ").lower().strip()
                if choice == 'y':
                    return "Duke"
                elif choice == 'n':
                    return None
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
        else:
            print(f"\n{self.name}, do you want to block the action {action.action_name} claiming any of the cards below?")
            block_options = action.can_block + ["Don't block"]
            for i, option in enumerate(block_options, 1):
                print(f"{i}. {option}")
            while True:
                choice = input("Enter the number of your choice: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(block_options):
                    selected_option = block_options[int(choice) - 1]
                    if selected_option == "Don't block":
                        return None
                    else:
                        return selected_option
                else:
                    print(f"Invalid input. Please enter a number between 1 and {len(block_options)}.")


    def add_card(self, card):
        """Adds a card to the players hand"""
        if self._is_eliminated:
            raise PlayerEliminatedError("Cannot add card to hand as player is eliminated!")
        if not card:
            raise GameException("Cannot add a null card to hand!")
        if len(self.hand) >= 2:
            raise HandIsFullError("Player cannot have more than 2 cards!")

        self.hand.append(card)

    def lose_coins(self, amount):
        """Lose a certain amount of coins from the players balance"""
        if amount > self.coins:
            raise NotEnoughCoinsError(f"{self.name} cannot lose more coins than they have.")
        self.coins -= amount

    def gain_coins(self, amount):
        """Player gains a certain amount of coins."""
        self.coins += amount

    def get_coins(self):
        return self.coins

    @property
    def is_eliminated(self):
        """A property method to return if the player is eliminated"""
        return self._is_eliminated

    def set_eliminated(self, eliminated):
        """Sets the player to eliminated"""
        if not isinstance(eliminated, bool):
            raise GameException("Eliminated status must be a boolean value!")
        self._is_eliminated = eliminated
        if eliminated:
            print(f"{self.name} is eliminated!")

    def lose_influence(self):
        """Makes the player choice what influence to lose if they have more than 1 card. Otherwise the player loses the remaining card"""
        if self.is_eliminated:
            raise PlayerEliminatedError("Cannot lose influence as player is eliminated!")
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")

        if len(self.hand) == 1:
            self.lose_card(0)
        else:
            self.choose_influence_to_die()

    def lose_card(self, card_index):
        """Makes the player lose the card"""
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")
        
        if card_index != 0 and card_index != 1:
            raise GameException("Invalid card index for losing influence!")
        
        if 0 <= card_index < len(self.hand):
            lost_card = self.hand.pop(card_index)
            self.influences_lost.append(lost_card.name)
            print(f"{self.name} has lost their {lost_card} influence.")
            if len(self.hand) == 0:
                self.set_eliminated(True)

            return lost_card.name

    def choose_influence_to_die(self):
        """Prompts the player to choose what card to eliminate"""
        print(f"{self.name}, you have the following cards:")
        self.display_cards(self.hand)

        while True:
            try:
                choice = int(input(f"{self.name}, select the influence you want to lose: ").strip())
                if choice == 1 or choice == 2:
                    self.lose_card(choice - 1)
                    break
                else:
                    print("Invalid choice, please choose a valid number.")
            except ValueError:
                print("Invalid choice, please choose a valid number.")

    def display_cards(self, cards):
        """Display the current cards in hand"""
        for i, card in enumerate(cards, start=1):
            print(f"{i}: {card}")

    def select_exchange_cards(self, drawn_cards):
        """Handles the action exchange which allows the player to draw upto 2 cards from the deck"""
        current_number_of_cards = len(self.hand)

        if len(self.hand) + len(drawn_cards) > 4:
            raise HandIsFullError("Player can have a max of 4 cards after exchange!")

        combined_hand = self.hand + drawn_cards
        print(f"{self.name}, you have drawn:")
        for card in drawn_cards:
            print(f"- {card}")

        returned_cards = self.choose_cards_to_return(combined_hand, len(drawn_cards))
        for card in returned_cards:
            combined_hand.remove(card)
        self.hand = combined_hand

        if len(self.hand) != current_number_of_cards:
            raise GameException(f"Error: Player's hand should have exactly {current_number_of_cards} cards after exchange.")

        print(f"{self.name}, your hand after exchange:")
        self.display_cards(self.hand)

        return returned_cards

    def choose_cards_to_return(self, combined_hand, num_drawn_cards):
        """Prompts the player to choose upto 2 cards to return back to the deck"""
        returned_cards = []
        while len(returned_cards) < num_drawn_cards:
            self.display_cards(combined_hand)
            choice = input("Select a card number to return: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(combined_hand):
                chosen_card = combined_hand[int(choice) - 1]
                if chosen_card in returned_cards:
                    print("You have already selected this card to return, choose another.")
                    continue
                returned_cards.append(chosen_card)
                print(f"{self.name} has returned the {chosen_card} card.")
            else:
                print("Invalid choice, please select a valid card number.")

        return returned_cards

    def has_card(self, card_name):
        """Checks if the player has the required card"""
        for card in self.hand:
            if card.name == card_name:
                return True
        return False

    def get_card_index(self, card_name):
        """Returns the index of the required card"""
        for index, card in enumerate(self.hand):
            if card.name == card_name:
                return index
        return None

    def swap_card(self, card_index):
        """Handles swapping the required card after the player has shown the card. Returns the required card back to the deck and gives the player a random card from the deck"""
        if self.game is None:
            raise GameException("Error: Player is not associated with a game.")
        if card_index < 0 or card_index >= len(self.hand):
            raise GameException("Invalid card index for swapping.")

        if 0 <= card_index < len(self.hand):
            removed_card = self.hand.pop(card_index) #first return card to deck then draw new card
            self.game.deck.return_card(removed_card)
            new_card = self.game.deck.draw_card()
            self.hand.append(new_card)
            print(f"{self.name} swapped a {removed_card} for a new card.")
        else:
            print("Invalid card index for swapping.")

    def prompt_show_card(self, card_name):
        """Prompts the player to show the card (in order to win the challenge or block)"""
        while True:
            decision = input(f"{self.name}, do you want to show the {card_name} card to win the challenge? (y/n): ").strip().lower()
            if decision == 'y':
                return True
            elif decision == 'n':
                return False
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")

    def wants_to_challenge(self, action, blocker=False):
        """Prompts the player to challenge. This method handles both the challenging and challenging the blocker (counter-challenge)"""
        if blocker:
            action_name = action  # Here, action is expected to be a string representing the blocker card
            message = f"\n{self.name}, do you want to challenge the block card {action_name}? (y/n): "
        else:
            action_name = action.action_name  # Here, action is an object, and we access its action_name attribute
            message = f"\n{self.name}, do you want to challenge the action {action_name}? (y/n): "
        
        print(message)
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return True
            elif decision == 'n':
                return False
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")

    def wants_to_block(self, action):
        """Prompts the player to block the action"""
        print(f"{self.name}, do you want to block {action.action_name}?")
        while True:
            decision = input("Type y for yes, n for no: ").strip().lower()
            if decision == 'y':
                return True
            elif decision == 'n':
                return False
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")

    def get_block_choice(self, block_options):
        """Displays all the possible block options for the player"""
        print(f"{self.name}, which card do you claim to block with?")
        for i, option in enumerate(block_options, 1):
            print(f"{i}: Claim {option}")

        while True:
            choice = input("Enter the number of the card you wish to claim: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(block_options):
                selected = block_options[int(choice) - 1]
                return selected
            else:
                print("Invalid choice, please select a valid card number.")

    def choose_action(self):
        """Shows all the valid actions a player can make and prompts them to select it. If target is required then it calls choose target"""
        actions = {
            "1": {"action": Income(self.game, self), "needs_target": False},
            "2": {"action": ForeignAid(self.game, self), "needs_target": False},
            "3": {"action": Coup(self.game, self, None), "needs_target": True},
            "4": {"action": Tax(self.game, self), "needs_target": False},
            "5": {"action": Assassinate(self.game, self, None), "needs_target": True},
            "6": {"action": Steal(self.game, self, None), "needs_target": True},
            "7": {"action": Exchange(self.game, self), "needs_target": False}
        }

        valid_actions = []

        for key, val in actions.items():
            action = val["action"]
            if action.coins_needed <= self.get_coins():
                valid_actions.append((key, val))

        if not valid_actions:
            print("You don't have enough coins to perform any action.")
            return None

        while True:
            print("\nNote: Some actions will require you to choose a target next.")
            print(f"{self.name}, choose an action:")
            for index, (key, val) in enumerate(valid_actions, start=1):
                action_note = "(needs to choose target next)" if val["needs_target"] else ""
                print(f"{index}: {val['action'].action_name} {action_note}")

            choice = input("Enter the number of the action you want to perform: ").strip()
            try:
                index = int(choice)
                if 1 <= index <= len(valid_actions):
                    selected_action, action_info = valid_actions[index - 1]
                    action = action_info['action']
                    needs_target = action_info['needs_target']
                    if needs_target:
                        target = self.choose_target()
                        if target is None:
                            print("No valid targets available. Please choose a different action.")
                            continue
                        action.target = target

                    return action
                else:
                    print("\nInvalid choice, please enter a valid number!")
            except ValueError:
                print("\nInvalid input, please enter a number!")
    
    def choose_target(self, action=None):
        """Prompts the player to choose a valid target for the chosen action"""
        valid_targets = []
        for x in self.game.players:
            if x != self and not x.is_eliminated:
                valid_targets.append(x)

        if not valid_targets:
            print("No valid targets available.")
            return None

        print("\nChoose a target:")
        for i, target in enumerate(valid_targets, 1):
            print(f"{i}: {target.name}")

        while True:
            try:
                choice = int(input(f"{self.name}, enter the number of the target you want to choose: ").strip())
                if 1 <= choice <= len(valid_targets):
                    return valid_targets[choice - 1]
                else:
                    print("Invalid choice, please select a number from the list.")
            except ValueError:
                print("Invalid input, please enter a number.")

    def __str__(self):
        return self.name
    
    def reset(self):
        self.hand = []
        self.coins = 2
        self._is_eliminated = False
        self.influences_lost = []