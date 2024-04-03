from exceptions.game_exceptions import *

class Player:
    """
    Represents a player in the Coup game, holding their cards, coins, and status.
    """

    def __init__(self, name):
        """
        Initializes a new player with a given name and default attributes.
        """
        self.name = name
        self.game = None
        self.reset()

    def reset(self):
        """
        Resets the player's state for a new game or round, with default cards, coins, and status.
        """
        self.hand = []  # Player's current hand of cards
        self.coins = 2  # Starting coins
        self._is_eliminated = False  # Player's elimination status
        self.influences_lost = []  # Tracks lost influences/cards

    def add_card(self, card):
        """
        Adds a card to the player's hand if they are not eliminated and have space.
        """
        if self._is_eliminated:
            raise PlayerEliminatedError("Cannot add card to hand as player is eliminated!")
        if not card:
            raise GameException("Cannot add a null card to hand!")
        if len(self.hand) >= 2:
            raise HandIsFullError("Player cannot have more than 2 cards!")

        self.hand.append(card)

    def lose_coins(self, amount):
        """
        Deducts a specified amount of coins from the player's total, if possible.
        """
        if amount > self.coins:
            raise NotEnoughCoinsError(f"{self.name} cannot lose more coins than they have.")
        self.coins -= amount

    def gain_coins(self, amount):
        """
        Adds a specified amount of coins to the player's total.
        """
        self.coins += amount

    def get_coins(self):
        """
        Returns the current amount of coins the player has.
        """
        return self.coins

    @property
    def is_eliminated(self):
        """
        Checks if the player has been eliminated from the game.
        """
        return self._is_eliminated

    def set_eliminated(self, eliminated):
        """
        Sets the player's elimination status, validating that the input is a boolean.
        """
        if not isinstance(eliminated, bool):
            raise GameException("Eliminated status must be a boolean value!")
        self._is_eliminated = eliminated
        if eliminated:
            print(f"{self.name} is eliminated!")

    def lose_influence(self): # Method always chosen.
        # User can choose to lose an influence. If only 1 card remains then that card is chosen
        """
        Processes the loss of an influence for the player, potentially eliminating them.
        """
        if self.is_eliminated:
            raise PlayerEliminatedError("Cannot lose influence as player is eliminated!")
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")

        if len(self.hand) == 1: 
            self.lose_card(0)  # Losing the last card
        else:
            self.choose_influence_to_die()

        

    def lose_card(self, card_index):
        """
        Removes a card from the player's hand based on the index, adding it to the lost influences.
        """
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")
        
        if card_index != 0 and card_index != 1:
            raise GameException("Invalid card index for losing influence!")
        
        lost_card = self.hand.pop(card_index)
        self.influences_lost.append(lost_card)
        print(f"{self.name} has lost their {lost_card} influence.")
        if len(self.hand) == 0:
            self.set_eliminated(True)

    def choose_influence_to_die(self):
        """
        Allows the player to choose which influence (card) to lose.
        """
        print(f"{self.name}, you have the following cards:")
        self.display_cards(self.hand)

        while True:
            try:
                choice = int(input(f"{self.name}, select the influence you want to lose: ").strip())
                if choice == 1 or choice == 2:
                    self.lose_card(choice - 1)  # Card index starts from 0
                    break
                else:
                    print("Invalid choice, please choose a valid number.")
            except ValueError:
                print("Invalid choice, please choose a valid number.")

            

    def display_cards(self, cards):
        """
        Displays the cards available in the player's hand.
        """
        for i, card in enumerate(cards, start=1):
            print(f"{i}: {card}")


    def select_exchange_cards(self, two_random_cards):
        """
        Allows the player to select cards to exchange from their hand with the deck.
        """
        current_number_of_cards = len(self.hand)

        if len(self.hand) + len(two_random_cards) > 4:
            raise HandIsFullError("Player can have a max of 4 cards after exchange!")

        combined_hand = self.hand + two_random_cards
        print(f"{self.name}, you have drawn:")
        for card in two_random_cards:
            print(f"- {card}")

        returned_cards = self.choose_cards_to_return(combined_hand)
        for card in returned_cards:
            combined_hand.remove(card)
        self.hand = combined_hand

        if len(self.hand) != current_number_of_cards:
            raise GameException(f"Error: Player's hand should have exactly {current_number_of_cards} cards after exchange.")

        print(f"{self.name}, your hand after exchange:")
        self.display_cards(self.hand)

        return returned_cards

    def choose_cards_to_return(self, combined_hand):
        """
        Helper method for select_exchange_cards to choose which cards to return to the deck.
        """
        returned_cards = []
        while len(returned_cards) < 2:
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
        """
        Checks if the player has a specific card in their hand.
        """
        for card in self.hand:
            if card.name == card_name:
                return True
        return False

    def get_card_index(self, card_name):
        """
        Returns the index of a specific card in the player's hand, if it exists.
        """
        for index, card in enumerate(self.hand):
            if card.name == card_name:
                return index
        return None

    def swap_card(self, card_index):
        """
        Swaps a specific card in the player's hand with a new one from the deck.
        """

        if self.game is None:
            raise GameException("Error: Player is not associated with a game.")
    
        if 0 <= card_index < len(self.hand):
            removed_card = self.hand.pop(card_index)
            new_card = self.game.deck.draw_card()
            self.hand.append(new_card)
            self.game.deck.return_card(removed_card)
            print(f"{self.name} swapped a {removed_card} for a new card.")
        else:
            print("Invalid card index for swapping.")

    def prompt_show_card(self, card_name):
        while True:
            decision = input(f"{self.name}, do you want to show the {card_name} card to win the challenge? (y/n): ").strip().lower()
            if decision == 'y':
                return True
            elif decision == 'n':
                return False
            else:
                print("Invalid input, please enter 'y' for yes or 'n' for no.")


    def __str__(self):
        """
        Returns a string representation of the player, primarily their name.
        """
        return self.name
