from player import Player
from cards.deck import Deck
from action import *

"""
TODO:
Implement the following:
- Initialising the game state
- Running the main game loop
- Handling player turns
- Handling player actions
- Handling player reactions (blocks, challenges and counteractions)
- For challenging, after a player wins the challenge, ensure that their card is shown and then returned to the deck, and a new card is drawn
- For assassin challenges, two cards can be lost if the challenge attempt is unsuccessful (lose challenge and action is played)
- Ensure that their is a counteraction. For example if target is challenged, they can counteract with a card. (e.g if assasssin action is played, they can block with contessa. This block can be challenged)
- Checking for game over conditions
- Handling game over
https://www.ultraboardgames.com/coup/game-rules.php
"""

#have a dictionary to display and store all lost influences (when eliminated) with the player name next to it
class Game:
    def __init__(self, number_of_players):
        self.players = []
        for i in range(1, number_of_players + 1):
            player_name = "Player " + str(i)
            self.players.append(Player(player_name))
        
        self.deck = Deck()
        self.current_turn = 0
        self.game_over = False
        self.active_player = self.players[self.current_turn]
        self.setup()

    def setup(self): 
        # Shuffle the deck, deal two cards to each player, and set starting coins
        self.deck.shuffle()
        for player in self.players:
            player.hand.append(self.deck.draw_card())
            player.hand.append(self.deck.draw_card())
            player.coins = 2

    # USE ADD CARD FROM PLAYER
    # def setup(self):
    # # Shuffle the deck, deal two cards to each player, and set starting coins
    # self.deck.shuffle()
    # for player in self.players:
    #     for _ in range(2):  # Assuming each player gets two cards initially
    #         card = self.deck.draw_card()
    #         player.add_card(card)
    #     player.coins = 2

    def run(self):
        # Main game loop
        while not self.game_over:
            self.active_player = self.players[self.current_turn]
            if not self.active_player.is_eliminated:
                self.execute_turn(self.active_player)
            self.check_game_over()
            self.current_turn = (self.current_turn + 1) % len(self.players)

    def execute_turn(self, player): 
        # Perform the actions of the current player's turn
        print(f"\n{player}'s turn.")
        chosen_action = self.choose_action(player)
        try:
            # Check for challenges here before executing the action
            self.handle_challenges(chosen_action)
            chosen_action.perform_action()
            # Check for blocks here after executing the action if not challenged or challenge failed
            self.handle_blocks(chosen_action)
        except GameException as e:
            print(str(e))
            # Depending on game rules, you may want to retry the turn or simply pass to the next player
            return
        
    def get_available_actions(self, player):
        actions = [Income(self, player), ForeignAid(self, player)]

        if player.coins >= 3:  # Assume 3 coins are needed to perform an Assassinate
            actions.append(Assassinate(self, player, None))  # Target is to be decided later

        if player.coins >= 7:  # Assume 7 coins are needed to perform a Coup
            actions.append(Coup(self, player, None))

        actions.extend([Tax(self, player), Steal(self, player, None), Exchange(self, player)])

        return actions
    
    def display_available_actions(self, player, available_actions):
        print(f"\n{player.name}, choose your action:")
        for index, action in enumerate(available_actions, 1):
            print(f"{index}. {action.__class__.__name__}")


    def choose_action(self, player):
        if player.coins >= 10:
            print("You have 10 or more coins and must perform a coup.")
            return Coup(self, player, self.choose_target(player))
    
        available_actions = self.get_available_actions(player)
        self.display_available_actions(player, available_actions)
    
        while True:
            choice = input("Choose your action: ")
            if choice.isdigit() and 0 < int(choice) <= len(available_actions):
                selected_action = available_actions[int(choice) - 1]
                if isinstance(selected_action, Coup):
                    target = self.choose_target(player)
                    if target:
                        return Coup(self, player, target)
                else:
                    return selected_action
            else:
                print("Invalid choice, please select a valid action.")


    def handle_blocks(self, action):
        if not action.blockable_by:
            return

        for player in self.players:
            if player != action.player and not player.is_eliminated:
                print(f"{player.name}, do you want to block this action? (yes/no)")
                decision = input().strip().lower()
                if decision == 'yes':
                    # Assuming a simplified block logic where the block is always successful
                    print(f"{player.name} has blocked the action!")
                    return True
        return False


    def handle_challenges(self, action):
        for player in self.players:
            if player != action.player and not player.is_eliminated:
                print(f"{player.name}, do you want to challenge this action? (yes/no)")
                decision = input().strip().lower()
                if decision == 'yes':
                    # Implement the challenge logic
                    print(f"{player.name} has challenged the action!")
                    if action.player.has_card(action.__class__.__name__):
                        print(f"Challenge failed. {action.player.name} has the {action.__class__.__name__}.")
                        # Handle the failure of the challenge
                    else:
                        print(f"Challenge succeeded. {action.player.name} does not have the {action.__class__.__name__}.")
                        # Handle the success of the challenge
                    return True
        return False
    
    def choose_target(self, acting_player):
        print("Choose a target for your action:")
        potential_targets = [p for p in self.players if p != acting_player and not p.is_eliminated]
        for i, player in enumerate(potential_targets, 1):
            print(f"{i}. {player.name}")

        while True:
            choice = input()
            if choice.isdigit() and 0 < int(choice) <= len(potential_targets):
                return potential_targets[int(choice) - 1]
            print("Invalid choice, please select a valid player.")





    def check_game_over(self):
        # Determine if the game is over and update self.game_over accordingly
        active_players = [p for p in self.players if not p.is_eliminated()]
        if len(active_players) == 1:
            self.game_over = True
            print(f"Game over! {active_players[0]} wins!")

if __name__ == "__main__":
    game = Game(num_players=4)
    game.run()


# class Game:
#     def __init__(self, players, deck):
#         self.players = players
#         self.deck = deck
#         self.current_player_index = 0
#         self.game_over = False

#     def start(self):
#         while not self.game_over:
#             current_player = self.players[self.current_player_index]
#             if not current_player.is_eliminated:
#                 self.execute_turn(current_player)
#             self.current_player_index = (self.current_player_index + 1) % len(self.players)
#             self.check_game_over()

#     def execute_turn(self, player):
#         print(f"\n{player.name}'s turn")
#         available_actions = self.get_available_actions(player)
#         chosen_action = self.choose_action(player, available_actions)
#         self.perform_action(chosen_action, player)

#     def get_available_actions(self, player):
#         # This would return a list of possible actions the player can perform
#         return [Income(player), ForeignAid(player), Coup(self, player, None)]  # Simplified example

#     def choose_action(self, player, available_actions):
#         # Here you would implement how a player chooses an action, possibly showing a menu
#         print(f"Available actions for {player.name}:")
#         for i, action in enumerate(available_actions, 1):
#             print(f"{i}. {action.__class__.__name__}")
#         choice = int(input("Choose an action: ")) - 1
#         return available_actions[choice]

#     def perform_action(self, action, player):
#         # Perform the chosen action and handle blocks and challenges
#         print(f"{player.name} has chosen to {action.__class__.__name__}")
#         action.perform_action()

#         # Check for reactions from other players (blocks or challenges)
#         for opponent in self.players:
#             if opponent != player and not opponent.is_eliminated:
#                 self.handle_reactions(action, opponent)

#     def handle_reactions(self, action, opponent):
#         # Placeholder for handling blocks and challenges from other players
#         pass

#     def check_game_over(self):
#         # Check if the game is over and set self.game_over appropriately
#         if len([player for player in self.players if not player.is_eliminated]) <= 1:
#             self.game_over = True
