"""
Defines the Player class for Coup. Each Player holds cards, coins, and makes decisions.
"""

#Go through and add exception raises. 
class Player:
    def __init__(self, name):
        self.name = name
        self.reset()  # Initialize or reset the player's state

    def reset(self):
        """
        Resets the player's state for a new game or round.
        """
        self.name = None #CHECK THIS LATER
        self.hand = []
        self.coins = 2
        self.is_eliminated = False

    def add_card(self, card):
        """
        Adds a card to the player's hand if there is space.
        """
        if len(self.hand) < 2:
            self.hand.append(card)

    def lose_influence(self):
        """
        Prompts the player to choose a card to lose when losing an influence.
        """
        if self.is_eliminated or not self.hand:
            return None

        print(f"{self.name}, select a card to lose:")

        for index, card in enumerate(self.hand, start=1):
            print(f"{index}: {card}")

        while True:
            try:
                choice = int(input("Choose a card number: ")) - 1
                if 0 <= choice < len(self.hand):
                    lost_card = self.hand.pop(choice)
                    print(f"{self.name} lost a {lost_card} influence.")
                    if not self.hand:
                        self.is_eliminated = True
                        print(f"{self.name} has been eliminated from the game.")
                    return lost_card
                else:
                    print("Invalid selection. Please choose a valid card number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def show_cards(self):
        """
        Returns a string representation of the player's hand of cards.
        """
        return ', '.join(str(card) for card in self.hand)

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return self.name
