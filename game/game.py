"""
Represents the main game class for Coup, handling the game state, player actions, and game flow.
"""

from players.player import Player
from players.ai_player import *
from cards.deck import Deck
from actions.action import *
from exceptions.game_exceptions import *
from game.log_manager import LogManager

class Game:
    """
    Initialises the game with a set of players and a deck of cards.
    """
    def __init__(self, deck):
        self.players = []
        self.deck = deck
        self.current_player_index = 0
        self.game_over = False
        self.current_round = 1
        self.log_manager = LogManager()
        self.last_action = None
        self.max_rounds = 100
    def setup(self):
        """
        Sets up the game by shuffling the deck and dealing cards and coins to each player.
        """
        self.deck.shuffle()
        for player in self.players:
            player.game = self
            player.add_card(self.deck.draw_card())
            player.add_card(self.deck.draw_card())

    def setup_ai_game(self, ai_players):
        """
        Sets up the AIPlayers for the game and adds cards to their hand.
        """
        self.deck.shuffle()
        for player in ai_players:
            player.game = self
            player.add_card(self.deck.draw_card())
            player.add_card(self.deck.draw_card())
        self.players = ai_players
        self.current_player_index = 0  # Set the current player index to 0
        for player in self.players:
            player.setup()

    def is_game_over(self):
        """
        Checks if the game is over, which happens if there is one player left.
        """
        return len(self.players_remaining()) <= 1
    
    def players_remaining(self):
        """
        Returns a list of players who are still in the game.
        """
        active_players = []
        for player in self.players:
            if not player.is_eliminated:
                active_players.append(player)
        return active_players
    
    def display_current_state(self):
        """
        Displays the current state of the game including players alive, their cards, and coins remaining.
        Also shows whose turn is next.
        """
        print("\nCurrent Game State:")
        print("=" * 30)
        print(f"Round: {self.current_round}")
        all_lost_influences = self.get_all_lost_influences()
        print(f"Total Influences Lost: {len(all_lost_influences)} ({', '.join(all_lost_influences)})")
        for player in self.players:
            if not player.is_eliminated:
                card_count = len(player.hand)
                coins = player.get_coins()
                print(f"{player.name}: Cards remaining: {card_count}, Coins remaining: {coins}")
        print("=" * 30)
        
        next_player = self.players[self.current_player_index]
        print(f"Next turn: {next_player.name}'s turn.")
        print("=" * 30)
        print()

    def log_action(self, player, action, target=None, challenge=None, challenge_outcome=None, blocker=None, blocker_claim=None, block_outcome=None, action_result=None, card_shown=None, card_eliminated=None):
        """
        Logs the details of each action and stores it to the action log.
        """
        log_entry = {
            'round': self.current_round,
            'player': player.name,
            'action': action.action_name if action else None,
            'target': target.name if target else None,
            'challenge': challenge.name if challenge else None,
            'challenge_outcome': challenge_outcome,
            'blocker': blocker.name if blocker else None,
            'blocker_claim': blocker_claim,
            'block_outcome': block_outcome,
            'action_result': action_result,
            'card_shown': card_shown,
            'card_eliminated': card_eliminated,
            'player_eliminated': player.is_eliminated,
            'target_eliminated': target.is_eliminated if target else None,
            'game_over': self.game_over,
            'player_coins': player.get_coins(),
            'target_coins': target.get_coins() if target else None,
            'remaining_players': [p.name for p in self.players_remaining()],
            'all_lost_influences': self.get_all_lost_influences()
        }
        self.log_manager.log_action(log_entry)

    def get_player_by_name(self, player_name):
        """
        Takes player name and returns the player object
        """
        for player in self.players:
            if player.name == player_name:
                return player
        return None
    
    def next_player(self):
        """
        Advances to the next player, skipping eliminated players.
        """
        print("\nNext player's turn\n")
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        while self.players[self.current_player_index].is_eliminated:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.current_player_index == 0:
                self.current_round += 1

    def end_game(self):
        """
        Ends the game and announces the winner.
        """
        self.game_over = True
        winner = self.players_remaining()[0]
        print(f"Game over! The winner is {winner.name}.")

    def force_coup(self, player):
        """
        Forces a coup if a player has 10 or more coins.
        """
        if player.get_coins() >= 10:
            print(f"{player.name} has 10 or more coins and must coup.")
            action = Coup(self, player, None)
            target = player.choose_target(action)
            action.target = target
            action.perform_action()
            card_eliminated = target.influences_lost[-1] if target.influences_lost else None
            self.log_action(player, action, target, action_result='performed', card_eliminated=card_eliminated if card_eliminated else None)

    def play_game(self):
        """
        Main game loop that continues until the game is over.
        """
        while not self.is_game_over():
            if self.current_round > self.max_rounds:
                print(f"Maximum number of rounds ({self.max_rounds}) reached. Terminating the game.")
                self.terminate_game()
                self.end_game()
                break
            self.display_current_state()
            self.play_turn(self.players[self.current_player_index])
            if self.game_over:
                break
            self.current_round += 1
            self.next_player()

        self.end_game()

    def terminate_game(self):
        """
        Determine the winner or declare a draw based on the game state.
        """
        # Sort players based on the number of cards remaining
        sorted_players = sorted(self.players, key=lambda p: len(p.hand), reverse=True)

        # Check if there is a clear winner based on the number of cards
        if len(sorted_players[0].hand) > len(sorted_players[1].hand):
            winner = sorted_players[0]
            print(f"{winner.name} wins with {len(winner.hand)} cards remaining!")
            return

        # If there is a tie based on the number of cards, sort by coins and check
        sorted_players.sort(key=lambda p: p.get_coins(), reverse=True)
        if sorted_players[0].get_coins() > sorted_players[1].get_coins():
            winner = sorted_players[0]
            print(f"{winner.name} wins with {winner.get_coins()} coins!")
            return

        # If there is still a tie, declare a draw
        print("It's a draw. All players have the same number of cards and coins!")

    def play_turn(self, player):
        """
        Executes a single turn for the given player.
        """
        print(f"{player.name}'s turn. Coins: {player.get_coins()}")
        player.display_cards(player.hand)
        player.turns_played += 1  # Increment turns_played
        self.force_coup(player)
        if not player.is_eliminated:
            self.execute_action(player)

    def execute_action(self, player, action=None):
        """
        Manages the execution of a player's action, including challenges and blocks.
        """
        if not action:
            action = player.choose_action()
        if action:
            player.actions_played += 1
            print(f"Debug: Action chosen - {action.action_name}, Target - {getattr(action.target, 'name', 'No Target')}")
            self.last_action = action
            target_description = f" on {action.target.name}" if action.target else ""
            print(f"\n{player.name} is attempting to perform {action.action_name}{target_description}.")

            action_result = 'not performed'
            challenge_outcome_result = None

            # If action requires an influence, then prompt players if they wish to challenge
            if action.requires_influence:
                challenger = self.prompt_challenge(player, action)
                # If there is a challenger
                if challenger:
                    challenger.challenges_made += 1
                    # Handle the challenge and return the result. (Handle challenge deals with losing influence, swapping card etc)
                    challenge_result, card_shown, card_eliminated = self.handle_challenge(player, challenger, action.required_card)
                    if not challenge_result: # If Challenger has won, The player has lost a card (handled above), and the turn has ended
                        challenge_outcome_result = 'challenge lost'
                        print(f"Turn ends. {challenger.name} has won the challenge.")
                        self.log_action(player, action, target=action.target, challenge=challenger, challenge_outcome=challenge_outcome_result, action_result=action_result, card_eliminated=card_eliminated, card_shown=card_shown)
                        return
                    else: # If player has won the challenge. (Challenger has lost an influence. this happened in handle challenge)
                        challenge_outcome_result = 'challenge won'
                        # Going to say action is performed due to the target being eliminated or game ends. So it can be techincally performed
                        if self.is_game_over(): # Check if 1 player remaining, if so then the game is over. (Turn ends here)
                            self.game_over = True
                            self.log_action(player, action, target=action.target, challenge=challenger, challenge_outcome=challenge_outcome_result, action_result='performed', card_eliminated=card_eliminated, card_shown=card_shown)
                            return
                        if action.target and action.target.is_eliminated: # If there is a target, and target is eliminated, then the turn ends.
                            action_result = 'target eliminated'
                            print(f"Turn ends. {action.target.name} has been eliminated.")
                            self.log_action(player, action, target=action.target, challenge=challenger, challenge_outcome=challenge_outcome_result, action_result='performed', card_eliminated=card_eliminated, card_shown=card_shown)
                            return
                        
            if action.is_blockable:
                self.handle_block_phase(action, player)
            else:
                self.log_action(player, action, action_result='performed')
                action.perform_action()

    def handle_block_phase(self, action, player):
        """
        Handles the block phase of the action section. Also allows for counter-challenges (challenging the blocker)
        """
        blocker, blocker_claim_card = self.prompt_block(player, action)

        # If there is a player who wishes to block (they become blocker)
        if blocker:
            blocker.blocks_made += 1
            print(f"{blocker.name} has chosen to block with {blocker_claim_card}.")
            # Prompts the player to counter the block (the player can choose if they want to challenge the blocker and the blockers card that they block with)
            if player.wants_to_challenge(blocker_claim_card, blocker):
                blocker_wins_challenge, card_shown, card_eliminated = self.handle_challenge(blocker, player, blocker_claim_card)
                if blocker_wins_challenge: # If the blocker wins the challenge against the player, the block is successful (blocker swaps their shown card and the player loses an influence)
                    self.log_action(player, action, target=action.target, challenge=player, challenge_outcome='challenge lost', action_result='not performed', blocker=blocker, blocker_claim=blocker_claim_card, block_outcome='blocker wins challenge', card_eliminated=card_eliminated, card_shown=card_shown)
                    print(f"Turn ends. {blocker.name} has successfully defended their claim and blocked the action.")
                    return
                else: # If the blocker has lost the challenge against the player, then the player can continue with the action as long as the blocker (target) is still alive.
                    if action.target and action.target.is_eliminated:
                        self.log_action(player, action, target=action.target, challenge=player, challenge_outcome='challenge won', action_result='target eliminated', blocker=blocker, blocker_claim=blocker_claim_card, block_outcome='blocker lost challenge', card_eliminated=card_eliminated, card_shown=card_shown)
                        print(f"Turn ends. {action.target.name} has been eliminated.")
                        return
                    else:
                        print(f"{player.name} has won the challenge and moves to perform {action.action_name}.")
                        self.log_action(player, action, target=action.target, challenge=player, challenge_outcome='challenge won', action_result='performed', blocker=blocker, blocker_claim=blocker_claim_card, block_outcome='blocker lost challenge', card_eliminated=card_eliminated, card_shown=card_shown)
                        action.perform_action()
                        return
            else: # The player does not wish to challenge the blocker, the turn ends here.
                print("Turn ends. Blocker's claim is unchallenged.")
                self.log_action(player, action, target=action.target, action_result='not performed', blocker=blocker, blocker_claim=blocker_claim_card, block_outcome='blocker not challenged')
                return
        else: # No blocker, so the player can perform the action
            print(f"No blocker, {player.name} will perform {action.action_name}.")
            self.log_action(player, action, target=action.target, action_result='performed')
            action.perform_action()
    
    def prompt_challenge(self, current_player, action):
        """
        Prompts for a challenge against a player's action.
        """
        for player in self.players_remaining():
            if player != current_player:
                if not player.is_human():
                    if player.wants_to_challenge(action):
                        print(f"{player.name} (AI) is challenging the action.")
                        return player
                    else:
                        print(f"{player.name} (AI) does not challenge the action.")
                else:
                    if player.wants_to_challenge(action):
                        print(f"{player.name} is challenging the action.")
                        return player
                    else:
                        print(f"{player.name} does not challenge the action.")

        return None
    
    def prompt_block(self, player, action):
        """
        Prompts for block against a player's action.
        """
        if action.action_name == "Foreign Aid": # Prompt block to all players, they can block claiming the Duke card.
            for potential_blocker in self.players_remaining():
                if potential_blocker != player:
                    # If the player is an AI
                    if not player.is_human():
                        print(f"\n{potential_blocker.name}, {player.name} is attempting Foreign Aid. Do you want to block by claiming Duke? (y/n)")
                        if potential_blocker.wants_to_block(action):
                            print(f"{potential_blocker.name} (AI) is blocking with Duke.")
                            return potential_blocker, "Duke"
                    else:
                        print(f"\n{potential_blocker.name}, {player.name} is attempting Foreign Aid. Do you want to block by claiming Duke? (y/n)")
                        if potential_blocker.wants_to_block(action):
                            return potential_blocker, "Duke"
                        else:
                            break
        else:
            if action.target and action.target != player: # Prompt block to only the target for the other actions.
                # If the target is an AI
                if not action.target.is_human():
                    print(f"\n{action.target.name}, do you want to block the action {action.action_name}?")
                    if action.target.wants_to_block(action):
                        chosen_card = action.target.get_block_choice(action.can_block)
                        if chosen_card:
                            print(f"{action.target.name} (AI) is blocking with {chosen_card}.")
                            return action.target, chosen_card
                    else:
                        print(f"{action.target.name} (AI) does not want to block.")
                else:
                    if action.target.wants_to_block(action):
                        chosen_card = action.target.get_block_choice(action.can_block)
                        if chosen_card:
                            print(f"{action.target.name} is blocking with {chosen_card}.")
                            return action.target, chosen_card
                    else:
                        print(f"{action.target.name} does not want to block.")
                        
        return None, None
    

    def handle_challenge(self, player, challenger, card_name):
        """
        Manages the challenge process between players over an action.
        Returns True if the player wins, False if the challenger wins.

        """
        card_shown = None
        card_eliminated = None
        challenge_result = False

        if player.has_card(card_name):
            #  If the  player has the card then they win the challenge
            card_shown = card_name
            print(f"\n{player.name} has successfully shown {card_name} and wins challenge.")
            player.swap_card(player.get_card_index(card_name))
            card_eliminated = challenger.lose_influence()
            challenge_result = True
            return challenge_result, card_shown, card_eliminated
        
        print(f"\n{player.name} does not have {card_name} and loses the challenge.")
        card_eliminated = player.lose_influence()
        return challenge_result, card_shown, card_eliminated

    def get_all_lost_influences(self):
        """
        Get all lost influences from all players to see which cards are out of the game.
        """
        all_lost_influences = []
        for player in self.players:
            all_lost_influences.extend(player.influences_lost)
        return all_lost_influences
    
    def get_player_public_state(self, player):
        """
        Get the public state of a specific player, which includes information that is
        visible to all players, but not the character cards they hold.
        """
        return {
            'coins': player.get_coins(),
            'card_count': len(player.hand),
            'is_eliminated': player.is_eliminated,
            'influences_lost': player.influences_lost
        }
    
    def get_game_state_for_ai(self, ai_player):
        """
        Get the overall state of the game for the AI including the action log
        """
        players_list = [{
            'name': player.name,
            'coins': player.get_coins(),
            'card_count': len(player.hand),
            'is_eliminated': player.is_eliminated,
            'influences_lost': player.influences_lost,
            'hand': [card.name for card in player.hand] if player == ai_player else None
        } for player in self.players]

        players_dict = {player['name']: player for player in players_list}

        return {
            'players_list': players_list,  # Keep the list for compatibility
            'players': players_dict,  # Add a dictionary for direct access
            'all_lost_influences': self.get_all_lost_influences(),
            'current_player': self.players[self.current_player_index].name,
            'deck_size': len(self.deck.cards),
            'action_log': self.log_manager.get_action_log(),  # Provide the complete action log
            'round': self.current_round
        }

    def reset(self):
        self.current_player_index = 0
        self.game_over = False
        self.current_round = 1
        self.last_action = None
        for player in self.players:
            player.reset()
        self.deck.reset()
        self.log_manager = LogManager()
        self.setup()