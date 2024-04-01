"""
Defines the Player class for Coup. Each Player holds cards, coins, and makes decisions.
"""

#Go through and add exception raises. 
# Make sure to have functions that also manage coins and influences

from exceptions.game_exceptions import *

class Player:
    def __init__(self, name):
        self.name = name
        self.reset()  # Initialize or reset the player's state

    def reset(self):
        """
        Resets the player's state for a new game or round.
        """
        self.hand = []
        self.coins = 2
        self._is_eliminated = False
        self.max_cards = 2
        self.influences_lost = []

        
    def add_card(self, card):
        """
        Adds a card to the player's hand if there is space.
        """
        if self._is_eliminated:
            raise PlayerEliminated("Cannot add card to hand as player is eliminated!")
        
        # if not card vs if card is none
        if not card:
            raise GameException("Cannot add a null card to hand!")

        if len(self.hand) >= self.max_cards:
            raise GameException("Player cannot have more than 2 cards!")
        
        self.hand.append(card)


    def lose_coins(self, amount):
        if amount > self.coins:
            raise NotEnoughCoins(f"{self.name} cannot lose more coins than they have.")
        self.coins -= amount

    def gain_coins(self, amount):
        self.coins += amount

    def get_coins(self):
        return self.coins

    #go through property decorators again
    @property
    def is_eliminated(self):
        return self._is_eliminated




    def set_eliminated(self, eliminated):
        if not isinstance(eliminated, bool):
            raise GameException("Cannot set eliminated to a non-boolean value!")
        self._is_eliminated = eliminated
        if eliminated:
            print(f"{self.name} is eliminated!")


    #should call choose influence to die
    def lose_influence(self):
        #do we do these logic checks too?
        if self.is_eliminated:
            raise PlayerEliminated("Cannot lose influence as player is eliminated!")
        if not self.hand:
            raise GameException("Cannot lose influence as player has no cards!")
            #self.check_eliminated()
        
        if len(self.hand) == 1:
            print(f"{self.name} has lost their last influence card: {self.hand[0]} and is eliminated!")
            self.influences_lost.append(self.hand.pop())
            self.set_eliminated(True)
        else:
            self.choose_influence_to_die()


        

    """
    It should be:
    choose influence to die:
        if player has 1 card:
            lose influence(card), print out card, print out player eliminated (or maybe do check eliminated?)
            lose influnce should also store the player lost card in influences_lost?
            eliminate player
        else:
            player is shown their hand, choose card to lose influence
            lose influence(card)
    """

    def choose_influence_to_die(self):
        print(f"{self.name}, select an influence to lose:")
        

        while True:
            try:
                print(self.display_cards(self.hand))
                choice = int(input("Select the influence you want to lose: "))
                
                if choice == 1 or choice == 2:
                    lost_card = self.hand.pop(choice -1)
                    self.influences_lost.append(lost_card)
                    print(f"{self.name} has lost their {lost_card} influence.") 
                    self.set_eliminated(True)
                    break
                    
                else:
                    print("Invalid choice, please choose either 1 or 2.")
                    
            except ValueError:
                print("Please input a number!")



    def display_cards(self, list_of_cards):
        display_cards_str = f"{self.name}, your current hand now includes:\n"

        for i, card in enumerate(list_of_cards, start=1):
            display_cards_str += f"{i}: {card}\n"

        return display_cards_str
    

    def select_exchange_cards(self, two_random_cards):
        if len(self.hand) + len(two_random_cards) > 4:
            raise GameException("Player can have a max of 4 cards after exchange!")

        # Add the two randomly drawn cards to the player's hand temporarily
        temp_hand = self.hand + two_random_cards

        print(f"{self.name}, you have drawn:")
        for card in two_random_cards:
            print(f"- {card} (newly drawn)")

        returned_cards = []

        while len(returned_cards) < 2:  # Ensure two cards are selected to return
            try:
                print(f"{self.name}, select a card to return (newly drawn cards are at the end):")
                print(self.display_cards(temp_hand))

                choice = int(input("Select a card number to return: "))
                if 1 <= choice <= len(temp_hand):
                    chosen_card = temp_hand[choice - 1]

                    if chosen_card in returned_cards:
                        print("You have already selected this card to return, choose another.")
                        continue

                    returned_cards.append(chosen_card)
                    temp_hand.remove(chosen_card)  # Remove from temp_hand to prevent reselection
                    print(f"{self.name} has returned the {chosen_card} card.")
                else:
                    print("Invalid choice, please select a valid card number.")
            except ValueError:
                print("Please input a number.")

        # Update player's hand by removing the returned cards and keeping the new ones
        self.hand = temp_hand

        if len(self.hand) != 2:
            raise GameException("Error: Player's hand should have exactly two cards after exchange.")

        print(f"{self.name}, your hand after exchange:")
        print(self.display_cards(self.hand))

        return returned_cards



    def get_card(self, index):
        return self.hand[index]

    
    def change_cards(self):
        pass

    def has_card(self, card_name):
        for card in self.hand:
            if card.name == card_name:
                return True
        return False


    def show_card(self, card_name):
        for index, card in enumerate(self.hand):
            if card.name == card_name:
                #print(f"{self.name} shows their {card.name} card.")
                return index  # Return the card's position
        return None  # Card not found

    def swap_card(self, card_index):
        if card_index is not None and 0 <= card_index < len(self.hand):
            removed_card = self.hand.pop(card_index)  # Remove the card from hand
            new_card = self.game.deck.draw_card()  # Assume the player has access to the game's deck
            self.hand.append(new_card)  # Add the new card to hand
            self.game.deck.return_card(removed_card)  # Return the old card to the deck
            print(f"{self.name} swapped a {removed_card.name} for a new card.")
            # Other necessary operations...
        else:
            print("Invalid card index for swapping.")
    

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return self.name
    

