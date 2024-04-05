from exceptions.game_exceptions import *
from game.player_new import Player
import random

class AIPlayer(Player):
    """
    AI version of a Player in the Coup game.
    """

    def __init__(self, name):
        super().__init__(name)

    def choose_action(self):
        """
        AI logic to choose the next action based on the game state and strategy.
        """
        # Example strategy: Choose a random action from available ones
        available_actions = self.get_available_actions()
        if available_actions:
            return random.choice(available_actions)
        return None

    def prompt_show_card(self, card_name):
        """
        AI decision-making for whether to show a card during a challenge.
        """
        # Simple AI logic: Show card if it has it, otherwise don't show
        return self.has_card(card_name)

    def get_available_actions(self):
        """
        Determine which actions the AI player can take based on the game state.
        """
        # Example: List all actions, but real logic should consider the game state
        actions = ['Income', 'ForeignAid', 'Coup']  # Should be actual action objects
        # Filter actions based on what the AI can afford or what makes sense in the current game state
        return actions

    def choose_influence_to_die(self):
        """
        AI logic to choose which influence (card) to lose when necessary.
        """
        if self.hand:
            return self.lose_card(0)  # Simplified logic: always lose the first card

    # Other decision-making methods can be overridden as needed
