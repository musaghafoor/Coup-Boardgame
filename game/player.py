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

    # # Not sure if i need this method. It sets eliminated based on certain things. Im confused about check eliminated and is_eliminated
    # def set_eliminated(self):
    #     # Update the _is_eliminated status based on game logic, such as hand size
    #     if len(self.hand) == 0 or self._is_eliminated:
    #         self._is_eliminated = True
    #         print(f"{self.name} is eliminated!")
    #         #maybe add print lost influences?
    

    # def set_eliminated(self, eliminated):
    #     if not isinstance(eliminated, bool):
    #         raise GameException("Cannot set eliminated to a non-boolean value!")
    #     self._is_eliminated = eliminated

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

    # def show_card(self):
    #     pass

    #Temporary solution?
    def show_card(self, card_index):
        """
        Allows the player to reveal one of their cards by index.
        Returns the card that was revealed.
        """
        if not self.hand:
            raise GameException(f"{self.name} has no cards to show.")
        if card_index < 0 or card_index >= len(self.hand):
            raise GameException("Invalid card index.")

        # Reveal the specified card.
        revealed_card = self.hand[card_index]
        print(f"{self.name} reveals a {revealed_card}.")
        return revealed_card

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return self.name
    

    # # Exchange cards with the Court. First take 2 random cards from the Court deck. 
    # # Choose which, if any, to exchange with your face-down cards. Then return two cards to the Court deck.
    # #draw two cards. Pick up your two cards. Shuffle them together so nobody knows what you are keeping, then return two of your choice to the deck (shuffle the deck afterwards).
    # def select_exchange_cards(self, two_random_cards):
    #     if len(self.hand) + len(two_random_cards)> 4:
    #         raise GameException("Player can have a max of 4 cards after exchange!")
    #     # Add the two randomly drawn cards to the player's hand
    #     self.hand.extend(two_random_cards)

    #     # Display all cards, indicating which ones are newly drawn
    #     print(f"{self.name}, you have drawn:")
    #     for card in two_random_cards:
    #         print(f"- {card} (newly drawn)")
        
    #     # print(f"{self.name}, your current hand now includes:")
    #     # for i, card in enumerate(self.hand, start=1): #consider adding newly drawn in the print statement next to the new cards
    #     #         print(f"{i}: {card}")
            
        
    #     returned_cards = []

    #     #for i in range(2): #prompt user to select two cards to return
    #     # while len(returned_cards) < 2: #ensures that the loop runs until two cards are returned
    #     #     try:
    #     #         print(self.display_cards())
    #     #         choice = int(input("Select a card number to return: "))
    #     #         if choice in range(1, len(self.hand) + 1):
    #     #             returned_card = self.hand.pop(choice - 1)
    #     #             returned_cards.append(returned_card)
    #     #             print(f"{self.name} you have returned the {returned_card} card.")
    #     #         else:
    #     #             print("Invalid choice, please select a valid card number.")
    #     #     except ValueError:
    #     #         print("Please input a number!")

    #     while len(returned_cards) < 2: #ensures that the loop runs until two cards are returned
    #         try:
    #             print(self.display_cards())
    #             choice = int(input("Select a card number to return: "))
    #             if choice in range(1, len(self.hand) + 1):
    #                 chosen_card = self.hand[choice - 1]
    #                 if chosen_card not in returned_cards:
    #                     returned_cards.append(chosen_card)
    #                     self.hand.remove(chosen_card)
    #                     print(f"{self.name} you have returned the {chosen_card} card.")
    #                 else:
    #                     print("You have already selected this card to return, choose another.")
    #             else:
    #                 print("Invalid choice, please select a valid card number.")
    #         except ValueError:
    #             print("Please input a number!")

    #     # print(f"{self.name}, your current hand now includes:")
    #     # for i, card in enumerate(self.hand, start=1):
    #     #         print(f"{i}: {card}")
                    
    #     self.hand = self.hand[-2:] #ensures that the  players hand only has two cards
    #     print(self.display_cards())

    #     return returned_cards

