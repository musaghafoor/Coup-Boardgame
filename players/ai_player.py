"""
Represents the ai class which inherits from the player class.
"""
import random
from collections import defaultdict
from players.player import Player
from actions.action import Income, Coup, ForeignAid, Tax, Assassinate, Steal, Exchange


class AIPlayerOldMonte(Player):
    """
    AIPlayer that uses Bayesian inference and Monte Carlo Simulation for initializing,
    and then relies heavily on a rule-based system to perform actions.
    """
    def __init__(self, name, game=None):
        super().__init__(name)
        self.game = game
        self.card_probabilities = None
        self.challenge_threshold = 2
        self.card_values = {
            "Duke": 5,
            "Captain": 4,
            "Contessa": 3,
            "Assassin": 2,
            "Ambassador": 1
        }
        self.last_actions = []

    def setup(self):
        """Setups the AIPlayer"""
        self.initialize_card_probabilities()

    def reset(self):
        """Resets the AIPlayer"""
        super().reset()
        self.initialize_card_probabilities()

    def is_human(self):
        """Differentiates between AI and Human players"""
        return False

    def initialize_card_probabilities(self):
        """Initializes the card probabilities"""
        if self.game:
            game_state = self.game.get_game_state_for_ai(self)
            self.card_probabilities = self.calculate_probabilities(game_state)

    def calculate_probabilities(self, game_state):
        """Calculates the card probabilities for each player card based on what cards the AI has."""
        deck_probabilities = self.get_deck_probabilities(game_state)
        total_cards_in_deck = sum(deck_probabilities.values())
        probabilities = {}

        for player_name in game_state["players"]:
            if player_name != self.name:
                player_probabilities = {}
                for card_name in ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]:
                    player_probabilities[card_name] = [deck_probabilities[card_name] / total_cards_in_deck] * 2
                probabilities[player_name] = player_probabilities

        return probabilities

    def get_deck_probabilities(self, game_state):
        """Adjusts the AI knowledge on the current cards remaining in play based on what cards the AI has and what cards are eliminated."""
        deck_probabilities = {
            "Duke": 3,
            "Assassin": 3,
            "Captain": 3,
            "Ambassador": 3,
            "Contessa": 3
        }

        for card in self.hand:
            deck_probabilities[card.name] -= 1

        for card_name in game_state["all_lost_influences"]:
            deck_probabilities[card_name] -= 1

        return deck_probabilities

    def update_card_probabilities(self, player, action, game_state):
        """Updates the card probabilities based on the action log information"""
        if action.action_result == 'performed' and not action.challenge:
            card_name = action.required_card

            for i in range(2):
                if self.card_probabilities[player.name][card_name][i] < 1:
                    self.card_probabilities[player.name][card_name][i] += 0.1
                    break

        if action.block_outcome == 'blocker not challenged' and not action.challenge:
            card_name = action.blocker_claim

            for i in range(2):
                if self.card_probabilities[player.name][card_name][i] < 1:
                    self.card_probabilities[player.name][card_name][i] += 0.1
                    break

        if action.card_shown:
            card_name = action.card_shown
            deck_probabilities = self.get_deck_probabilities(game_state)
            deck_probabilities[card_name] += 1
            total_cards_in_deck = sum(deck_probabilities.values())

            for card in ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]:
                for i in range(2):
                    self.card_probabilities[player.name][card][i] = deck_probabilities[card] / total_cards_in_deck

        for player_name in self.card_probabilities:
            for card in self.card_probabilities[player_name]:
                total_probability = sum(self.card_probabilities[player_name][card])
                for i in range(2):
                    self.card_probabilities[player_name][card][i] /= total_probability

        simulated_probabilities = self.monte_carlo_simulation(game_state)
        for player_name in simulated_probabilities:
            for card_name in simulated_probabilities[player_name]:
                for i in range(2):
                    self.card_probabilities[player_name][card_name][i] = (
                        self.card_probabilities[player_name][card_name][i] + simulated_probabilities[player_name][card_name][i]
                    ) / 2

    def choose_action(self):
        game_state = self.game.get_game_state_for_ai(self)
        available_actions = self.get_available_actions(game_state)

        # Evaluate actions based on game state and probabilities
        action_scores = self.evaluate_actions(game_state, available_actions)

        # Check if the last 3 actions are the same
        if len(self.last_actions) >= 3 and len(set(self.last_actions[-3:])) == 1:
            # Choose the 2nd best action
            sorted_actions = sorted(available_actions, key=lambda action: action_scores[action.action_name], reverse=True)
            if len(sorted_actions) > 1:
                best_action = sorted_actions[1]
            else:
                best_action = sorted_actions[0]
        else:
            # Choose the action with the highest score
            best_action = max(available_actions, key=lambda action: action_scores.get(action.action_name, float('-inf')))

        if best_action.needs_target:
            best_target = self.choose_target(best_action)
            if best_target is None:
                available_actions.remove(best_action)
                if available_actions:
                    return self.choose_action()
                else:
                    return None
            best_action.target = best_target

        self.last_actions.append(best_action.action_name)
        return best_action

    def choose_target(self, action=None):
        """Chooses the best target available. This is calculated in evaluate_target"""
        game_state = self.game.get_game_state_for_ai(self)

        if action:
            available_targets = self.get_available_targets(game_state, action.action_name)
        else:
            available_targets = self.get_available_targets(game_state, None)

        if not available_targets:
            return None

        if action.action_name == "Coup":
            best_target, _ = self.evaluate_targets(game_state, action)
        else:
            best_target, _ = self.evaluate_targets(game_state, action)

        for player in self.game.players:
            if player.name == best_target['name']:
                return player

        return None

    def wants_to_challenge(self, action, blocker=False):
        """Decides whether to challenge or not challenge the action/blocker"""
        game_state = self.game.get_game_state_for_ai(self)
        low_chance = 0.3  # Probability threshold below which AI will challenge

        if blocker:
            action_name = action
            player = blocker.name
        else:
            action_name = action.required_card
            player = action.player.name

        # If the AI has only one card left, it needs to be more cautious
        if len(self.hand) == 1:
            if action_name == "Assassin":
                if not self.has_card("Contessa"):
                    if self.card_probabilities is not None:
                        return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
                    else:
                        return True
            elif action_name == "Steal":
                if not (self.has_card("Ambassador") or self.has_card("Captain")):
                    if self.card_probabilities is not None:
                        return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
                    else:
                        return True

        if game_state['round'] >= self.challenge_threshold:
            if self.card_probabilities is not None:
                return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
            else:
                return False

        return False

    def wants_to_block(self, action):
        """Decides whether or not to block the action"""
        for card_name in action.can_block:
            if self.has_card(card_name):
                return True

        if len(self.hand) == 1:
            if action.action_name == "Assassinate":
                return True

        return False

    def get_block_choice(self, block_options):
        """Gets the required block cards for the action and presents it"""
        for card_name in block_options:
            if self.has_card(card_name):
                return card_name

        return random.choice(block_options)

    def get_available_actions(self, game_state):
        """Gets the available actions that can be performed"""
        actions = [Income(self.game, self), ForeignAid(self.game, self), Tax(self.game, self), Exchange(self.game, self)]

        if self.get_coins() >= 3:
            if any(self.get_available_targets(game_state, "Assassinate")):
                actions.append(Assassinate(self.game, self, None))

        if self.get_coins() >= 7:
            if any(self.get_available_targets(game_state, "Coup")):
                actions.append(Coup(self.game, self, None))

        if any(self.get_available_targets(game_state, "Steal")):
            actions.append(Steal(self.game, self, None))

        return actions

    def get_available_targets(self, game_state, action_name, min_coins=0):
        """Gets all valid targets for the chosen action"""
        available_targets = []

        for player in game_state['players'].values():
            if player['name'] != self.name and not player['is_eliminated']:
                if action_name == "Steal" and player['coins'] < min_coins:
                    continue
                available_targets.append(player)

        return available_targets

    def evaluate_actions(self, game_state, actions):
        """Evaluates the actions based on set criteria, using a scoring system for each action"""
        action_scores = {}

        for action in actions:
            score = 0

            if action.action_name == "Coup":
                score += 5

            if action.action_name == "Tax" and self.has_card("Duke"):
                score += 2

            if action.action_name in ["Assassinate", "Steal"]:
                best_target, target_score = self.evaluate_targets(game_state, action)
                if self.has_card(action.required_card):
                    score += target_score
                else:
                    score -= 2

            if action.action_name == "Exchange":
                card_score = sum(self.card_values[card.name] for card in self.hand)
                if card_score < 5:
                    score += 2

            if action.action_name in ["Income", "Foreign Aid"]:
                score += 1

            action_scores[action.action_name] = score

        return action_scores

    def evaluate_targets(self, game_state, action):
        """Evaluates all the targets on set criteria, using a scoring system"""
        target_scores = {}
        best_target = None
        best_score = float('-inf')

        for target in self.get_available_targets(game_state, action.action_name):
            score = 0
            player_data = game_state['players'][target['name']]

            if len(player_data['influences_lost']) == 1:
                score += 1
                score += player_data['coins'] / 10

            if action.action_name == "Coup":
                if len(player_data['influences_lost']) == 1:
                    score += player_data['coins'] / 5
                else:
                    score += player_data['coins'] / 10

            if action.action_name == "Assassinate":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for i in range(2):
                        block_probability += self.card_probabilities[target['name']]["Contessa"][i]
                    score -= block_probability * 2
                else:
                    score -= 0.5

            if action.action_name == "Steal":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for card in ["Captain", "Ambassador"]:
                        for i in range(2):
                            block_probability += self.card_probabilities[target['name']][card][i]
                    score -= block_probability * 2
                else:
                    score -= 0.5

            if score > best_score:
                best_target = target
                best_score = score

            target_scores[target['name']] = score

        return best_target, best_score

    def choose_influence_to_die(self):
        """Chooses what influence to lose if the AI has more than 1 card. Otherwise lose the remaining card"""
        if len(self.hand) == 1:
            print(f"{self.name} is losing their last influence.")
            return self.lose_card(0)

        card_scores = []
        for card in self.hand:
            card_scores.append(self.card_values[card.name])

        min_score_index = card_scores.index(min(card_scores))
        print(f"{self.name} is choosing to lose the {self.hand[min_score_index]} influence.")
        return self.lose_card(min_score_index)

    def select_exchange_cards(self, drawn_cards):
        """Choose what cards to keep from the exchange action"""
        combined_cards = self.hand + drawn_cards
        card_scores = []
        for card in combined_cards:
            card_scores.append(self.card_values[card.name])

        if len(drawn_cards) == 1:
            if card_scores[-1] > min(card_scores[:-1]):
                kept_cards = [combined_cards[-1]]
                removed_index = card_scores[:-1].index(min(card_scores[:-1]))
                for i in range(len(self.hand)):
                    if i != removed_index:
                        kept_cards.append(self.hand[i])
                self.hand = kept_cards
                returned_cards = [combined_cards[removed_index]]
            else:
                returned_cards = [combined_cards[-1]]
        else:
            sorted_indices = sorted(range(len(card_scores)), key=lambda i: card_scores[i], reverse=True)
            selected_indices = sorted_indices[:2]
            self.hand = []
            for i in selected_indices:
                self.hand.append(combined_cards[i])
            returned_cards = []
            for i, card in enumerate(combined_cards):
                if i not in selected_indices:
                    returned_cards.append(card)

        print(f"{self.name} is choosing to keep {[card.name for card in self.hand]} and return {[card.name for card in returned_cards]}.")
        return returned_cards

    def prompt_show_card(self, card_name):
        """Shows the card if the AI has it in the hand, otherwise don't show and lose challenge"""
        if self.has_card(card_name):
            print(f"{self.name} is showing the {card_name} card to win the challenge.")
            return True
        else:
            print(f"{self.name} does not have the {card_name} card and loses the challenge.")
            return False

    def prompt_challenge(self, action):
        """Prompts the AI to challenge the action. The logic to handle the decision is in wants_to_challenge"""
        if self.wants_to_challenge(action):
            print(f"{self.name} is challenging the {action.action_name} action.")
            return True
        else:
            print(f"{self.name} is not challenging the {action.action_name} action.")
            return False

    def prompt_block(self, action):
        """Prompts the AI to block the action. The logic to handle the decision is in wants_to_block"""
        if self.wants_to_block(action):
            block_choice = self.get_block_choice(action.can_block)
            print(f"{self.name} is blocking the {action.action_name} action with {block_choice}.")
            return block_choice
        else:
            print(f"{self.name} is not blocking the {action.action_name} action.")
            return None

    def monte_carlo_simulation(self, game_state, num_simulations=500):
        """Runs a monte carlo simulation for num_simulation times"""
        simulated_probabilities = defaultdict(lambda: defaultdict(lambda: [0] * 2))

        for _ in range(num_simulations):
            simulated_state = self.simulate_game_state(game_state)
            simulated_action_log = self.simulate_action_log(simulated_state, game_state["action_log"])
            updated_probabilities = self.update_probabilities_from_action_log(simulated_state, simulated_action_log)

            for player_name in updated_probabilities:
                for card_name in updated_probabilities[player_name]:
                    simulated_probabilities[player_name][card_name][0] += updated_probabilities[player_name][card_name][0]
                    simulated_probabilities[player_name][card_name][1] += updated_probabilities[player_name][card_name][1]

        for player_name in simulated_probabilities:
            for card_name in simulated_probabilities[player_name]:
                if num_simulations > 0:
                    simulated_probabilities[player_name][card_name][0] /= num_simulations
                    simulated_probabilities[player_name][card_name][1] /= num_simulations
                else:
                    simulated_probabilities[player_name][card_name] = [0, 0]

        return simulated_probabilities

    def simulate_game_state(self, game_state):
        """Simulates the game state to decide what decisions are good"""
        simulated_state = {
            "players": {},
            "all_lost_influences": game_state["all_lost_influences"][:],
        }

        remaining_cards = self.get_remaining_cards(game_state)
        random.shuffle(remaining_cards)

        for player_name in game_state["players"]:
            if player_name != self.name:
                player_hand = remaining_cards[:2]
                remaining_cards = remaining_cards[2:]
                simulated_state["players"][player_name] = {
                    "hand": player_hand,
                    "coins": game_state["players"][player_name]["coins"],
                    "is_eliminated": game_state["players"][player_name]["is_eliminated"],
                    "influences_lost": game_state["players"][player_name]["influences_lost"][:],
                }
            else:
                simulated_state["players"][player_name] = {
                    "hand": [card.name for card in self.hand],
                    "coins": self.get_coins(),
                    "is_eliminated": self.is_eliminated,
                    "influences_lost": self.influences_lost[:],
                }

        return simulated_state

    def simulate_action_log(self, simulated_state, action_log):
        """Simulates all the log entries in the action log"""
        simulated_action_log = []
        for action in action_log:
            simulated_action = action.copy()
            if action["player"] != self.name:
                simulated_action["player"] = action["player"]
            if action["target"] is not None and action["target"] != self.name:
                simulated_action["target"] = action["target"]
            simulated_action_log.append(simulated_action)
        return simulated_action_log

    def update_probabilities_from_action_log(self, simulated_state, simulated_action_log):
        """Update the probabilities of each player card based on the action log"""
        updated_probabilities = defaultdict(lambda: defaultdict(lambda: [0] * 2))

        for action in simulated_action_log:
            player_name = action["player"]
            target_name = action["target"]
            action_name = action["action"]
            challenge = action["challenge"]
            challenge_outcome = action["challenge_outcome"]
            blocker = action["blocker"]
            blocker_claim = action["blocker_claim"]
            block_outcome = action["block_outcome"]
            card_shown = action["card_shown"]

            if action_name in ["Tax", "Assassinate", "Steal", "Exchange"]:
                if challenge is None and block_outcome is None:
                    updated_probabilities[player_name][action_name][0] += 1
                elif challenge is not None and challenge_outcome == "challenge_lost":
                    updated_probabilities[player_name][action_name][0] += 1
                    updated_probabilities[challenge][action_name][0] -= 1
                elif block_outcome == "block_failed":
                    updated_probabilities[player_name][action_name][0] += 1
                    updated_probabilities[blocker][blocker_claim][0] -= 1

            if card_shown is not None:
                updated_probabilities[player_name][card_shown][0] = 1
                updated_probabilities[player_name][card_shown][1] = 0

        return updated_probabilities

    def get_remaining_cards(self, game_state):
        """Gets the remaining cards"""
        all_cards = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"] * 3
        for player_data in game_state["players"].values():
            if "hand" in player_data:
                for card in player_data["hand"]:
                    all_cards.remove(card)
        for card_name in game_state["all_lost_influences"]:
            all_cards.remove(card_name)
        return all_cards
    


class AIPlayerMonte(Player):
    """
    AIPlayerMonte is an AI player that uses a combination of probabilistic reasoning and Monte Carlo
    simulations to make decisions in the game.
    """

    def __init__(self, name, game=None):
        """
        Initialize the AIPlayerMonte with the given name and game.
        """
        super().__init__(name)
        self.game = game
        self.card_probabilities = None  # Probabilities of opponent cards
        self.challenge_threshold = 0.3  # Threshold for challenging actions
        self.bluff_threshold = 0.4  # Threshold for bluffing blocks
        self.block_threshold = 0.5  # Threshold for blocking actions
        self.card_values = {
            "Duke": 5,
            "Captain": 4,
            "Contessa": 3,
            "Assassin": 2,
            "Ambassador": 1
        }  # Card value mapping for decision-making
        self.action_weights = {
            "Income": 1,
            "Foreign Aid": 2,
            "Coup": 6,
            "Tax": 3,
            "Assassinate": 4,
            "Steal": 4,
            "Exchange": 2
        }  # Action weight mapping for evaluation
        self.last_actions = []

    def setup(self):
        """
        Setup the AIPlayerMonte by initializing the card probabilities.
        """
        self.initialize_card_probabilities()

    def reset(self):
        """
        Reset the AIPlayerMonte by resetting its parent class and re-initializing the card probabilities.
        """
        super().reset()
        if self.game is not None:
            self.initialize_card_probabilities()

    def initialize_card_probabilities(self):
        """
        Initialize the card probabilities for all opponent players based on the current game state.
        """
        game_state = self.game.get_game_state_for_ai(self)
        self.card_probabilities = self.calculate_probabilities(game_state)

    def calculate_probabilities(self, game_state):
        """
        Calculate the probabilities of opponent cards based on the current game state.
        """
        deck_probabilities = self.get_deck_probabilities(game_state)
        total_cards_in_deck = sum(deck_probabilities.values())
        probabilities = {}

        for player_name, player_data in game_state["players"].items():
            if player_name != self.name:
                player_probabilities = {}
                for card_name in ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]:
                    player_probabilities[card_name] = [
                        deck_probabilities[card_name] / total_cards_in_deck,
                        deck_probabilities[card_name] / total_cards_in_deck
                    ]
                probabilities[player_name] = player_probabilities

        return probabilities

    def get_deck_probabilities(self, game_state):
        """
        Get the probabilities of cards remaining in the deck based on the current game state.
        """
        deck_probabilities = {
            "Duke": 3,
            "Assassin": 3,
            "Captain": 3,
            "Ambassador": 3,
            "Contessa": 3
        }

        # Subtract cards in the AI's hand from the deck probabilities
        for card in self.hand:
            deck_probabilities[card.name] -= 1

        # Subtract lost cards from the deck probabilities
        for card_name in game_state["all_lost_influences"]:
            deck_probabilities[card_name] -= 1

        return deck_probabilities

    def update_card_probabilities(self, action_log):
        """
        Update the card probabilities for all players based on the action log.
        """
        if not self.card_probabilities or not action_log:
            return

        for log_entry in action_log:
            player_name = log_entry["player"]
            action_name = log_entry["action"]
            challenge = log_entry["challenge"]
            challenge_outcome = log_entry["challenge_outcome"]
            blocker = log_entry["blocker"]
            blocker_claim = log_entry["blocker_claim"]
            block_outcome = log_entry["block_outcome"]
            card_shown = log_entry["card_shown"]

            if player_name is not None and player_name != self.name:
                if challenge is None and block_outcome is None:
                    if action_name in ["Tax", "Assassinate", "Steal", "Exchange"]:
                        self.card_probabilities[player_name][action_name][0] *= 1.2
                        self.card_probabilities[player_name][action_name][1] *= 1.2
                elif block_outcome == "blocker not challenged":
                    if blocker != self.name:
                        self.card_probabilities[blocker][blocker_claim][0] *= 1.2
                        self.card_probabilities[blocker][blocker_claim][1] *= 1.2
                elif challenge is not None:
                    if challenge != self.name:
                        if challenge_outcome == "challenge_won":
                            self.card_probabilities[player_name][action_name][0] *= 0.8
                            self.card_probabilities[player_name][action_name][1] *= 0.8
                        elif challenge_outcome == "challenge_lost":
                            self.card_probabilities[challenge][action_name][0] *= 0.8
                            self.card_probabilities[challenge][action_name][1] *= 0.8

            if card_shown is not None:
                self.card_probabilities[player_name][card_shown] = [1, 0]

        self.normalize_probabilities()
        self.update_probabilities_with_monte_carlo(action_log)

    def normalize_probabilities(self):
        """
        Normalize the card probabilities for all players.
        """
        # GPT solution to normalizing probabilities
        for player_name, probs in self.card_probabilities.items():
            total_probability = sum(sum(probab) for probab in probs.values())
            if total_probability > 0:
                for card, probab in probs.items():
                    probs[card] = [
                        probab[0] / total_probability,
                        probab[1] / total_probability
                    ]

    def update_probabilities_with_monte_carlo(self, action_log):
        """
        Update the card probabilities using Monte Carlo simulations.
        """
        game_state = self.game.get_game_state_for_ai(self)
        simulated_probabilities = self.monte_carlo_simulation(game_state, action_log)

        for player_name in simulated_probabilities:
            for card_name in simulated_probabilities[player_name]:
                self.card_probabilities[player_name][card_name][0] = (
                    self.card_probabilities[player_name][card_name][0] + simulated_probabilities[player_name][card_name][0]
                ) / 2
                self.card_probabilities[player_name][card_name][1] = (
                    self.card_probabilities[player_name][card_name][1] + simulated_probabilities[player_name][card_name][1]
                ) / 2

    def choose_action(self):
        game_state = self.game.get_game_state_for_ai(self)
        action_log = game_state["action_log"]

        self.update_card_probabilities(action_log)

        available_actions = self.get_available_actions(game_state)
        valid_actions = []
        for action in available_actions:
            if self.can_perform_action(action):
                valid_actions.append(action)

        if not valid_actions:
            return None

        action_scores = self.evaluate_actions(game_state, valid_actions)

        # Check if the last 3 actions are the same
        if len(self.last_actions) >= 3 and len(set(self.last_actions[-3:])) == 1:
            # Choose the 2nd best action
            sorted_actions = sorted(valid_actions, key=lambda action: action_scores[action.action_name], reverse=True)
            if len(sorted_actions) > 1:
                chosen_action = sorted_actions[1]
            else:
                chosen_action = sorted_actions[0]
        else:
            chosen_action = max(valid_actions, key=lambda action: action_scores.get(action.action_name, float('-inf')))

        if chosen_action.needs_target:
            best_target = self.choose_target(chosen_action)
            if best_target is None:
                valid_actions.remove(chosen_action)
                if valid_actions:
                    return self.choose_action()
                else:
                    return None
            chosen_action.target = best_target

        self.last_actions.append(chosen_action.action_name)
        return chosen_action

    def can_perform_action(self, action):
        """
        Check if the given action can be performed based on the game state.
        """
        if action.coins_needed > self.get_coins():
            return False
        if action.needs_target and not self.get_available_targets(self.game.get_game_state_for_ai(self), action.action_name):
            return False
        if action.requires_influence and not self.has_card(action.required_card):
            return False
        return True

    def choose_target(self, action=None):
        """
        Choose the best target for the given action based on probabilistic reasoning.
        """
        game_state = self.game.get_game_state_for_ai(self)
        action_log = game_state["action_log"]

        self.update_card_probabilities(action_log)

        if action:
            available_targets = self.get_available_targets(game_state, action.action_name)
        else:
            available_targets = self.get_available_targets(game_state, None)

        if not available_targets:
            return None

        if action.action_name == "Coup":
            best_target, _ = self.evaluate_targets(game_state, action)
        else:
            best_target, _ = self.evaluate_targets(game_state, action)

        if best_target is None:
            return None

        for player in self.game.players:
            if player.name == best_target["name"]:
                return player

        return None

    def wants_to_challenge(self, action, blocker=False):
        """
        Decide whether to challenge an action or a blocker's claim based on probabilistic reasoning.
        """
        game_state = self.game.get_game_state_for_ai(self)
        action_log = game_state["action_log"]

        self.update_card_probabilities(action_log)

        if blocker:
            action_name = action
            player = blocker.name
        else:
            action_name = action.required_card
            player = action.player.name

        if self.card_probabilities is None or player not in self.card_probabilities:
            return False

        if len(self.hand) == 1:
            if action_name == "Assassin":
                if not self.has_card("Contessa"):
                    for i in range(2):
                        if self.card_probabilities[player].get(action_name, [1, 1])[i] < self.challenge_threshold:
                            return True
            elif action_name == "Steal":
                if not (self.has_card("Ambassador") or self.has_card("Captain")):
                    for i in range(2):
                        if self.card_probabilities[player].get(action_name, [1, 1])[i] < self.challenge_threshold:
                            return True

        for i in range(2):
            if self.card_probabilities[player].get(action_name, [1, 1])[i] < self.challenge_threshold:
                return True

        return False

    def wants_to_block(self, action):
        """
        Decide whether to block an action based on probabilistic reasoning.
        """
        game_state = self.game.get_game_state_for_ai(self)
        action_log = game_state["action_log"]

        self.update_card_probabilities(action_log)

        for card_name in action.can_block:
            if self.has_card(card_name):
                return True
            elif self.card_probabilities and action.player.name in self.card_probabilities and action.required_card in self.card_probabilities[action.player.name]:
                for i in range(2):
                    if self.card_probabilities[action.player.name].get(action.required_card, [1, 1])[i] < self.block_threshold:
                        return True

        if len(self.hand) == 1:
            if action.action_name == "Assassinate":
                return True

        return False

    def get_block_choice(self, block_options):
        """
        Get the required block card for the action, or choose a random card to bluff.
        """
        for card_name in block_options:
            if self.has_card(card_name):
                return card_name

        return random.choice(block_options)

    def get_available_actions(self, game_state):
        """
        Get the available actions that the AI can perform based on the game state.
        """
        actions = [Income(self.game, self), ForeignAid(self.game, self), Tax(self.game, self), Exchange(self.game, self)]

        if self.get_coins() >= 3:
            if any(self.get_available_targets(game_state, "Assassinate")):
                actions.append(Assassinate(self.game, self, None))

        if self.get_coins() >= 7:
            if any(self.get_available_targets(game_state, "Coup")):
                actions.append(Coup(self.game, self, None))

        if any(self.get_available_targets(game_state, "Steal", min_coins=2)):
            actions.append(Steal(self.game, self, None))

        return actions

    def get_available_targets(self, game_state, action_name, min_coins=0):
        """
        Get all valid targets for the chosen action based on the game state.
        """
        available_targets = []

        for player_data in game_state['players'].values():
            if player_data['name'] != self.name and not player_data['is_eliminated']:
                if action_name == "Steal" and player_data['coins'] < 2:
                    continue
                if action_name != "Steal" and player_data['coins'] < min_coins:
                    continue
                available_targets.append(player_data)

        return available_targets

    def evaluate_actions(self, game_state, actions):
        """
        Evaluate the available actions based on predefined weights and probabilistic reasoning.
        """
        action_scores = {}
        num_players = len(game_state['players'])
        hand_score = 0
        for card in self.hand:
            hand_score += self.card_values[card.name]

        for action in actions:
            score = self.action_weights[action.action_name]

            if action.action_name == "Coup":
                if num_players <= 2:
                    score *= 2
                else:
                    score *= 1.5

            if action.action_name == "Tax" and self.has_card("Duke"):
                score *= 1.5

            if action.action_name == "Exchange":
                if num_players <= 2:
                    score *= 1.2
                if hand_score < 6:
                    score *= 1.5
                else:
                    score *= 0.8

            if action.action_name in ["Assassinate", "Steal"]:
                best_target, target_score = self.evaluate_targets(game_state, action)
                if self.has_card(action.required_card):
                    score += target_score
                else:
                    score -= 2

            if action.action_name in ["Income", "Foreign Aid"]:
                if num_players > 3:
                    score *= 0.9
                else:
                    score *= 1.1

            action_scores[action.action_name] = score

        return action_scores

    def evaluate_targets(self, game_state, action):
        """
        Evaluate all the targets for the given action based on probabilistic reasoning.
        """
        target_scores = {}
        best_target = None
        best_score = float('-inf')

        for target in self.get_available_targets(game_state, action.action_name):
            score = 0

            if len(target['influences_lost']) == 1:
                score += 2
                score += target['coins'] / 5

            if action.action_name == "Coup":
                if len(target['influences_lost']) == 1:
                    score += target['coins'] / 3
                else:
                    score += target['coins'] / 5

            if action.action_name == "Assassinate":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for i in range(2):
                        block_probability += self.card_probabilities[target['name']]["Contessa"][i]
                    score -= block_probability * 2
                    score += target['coins'] / 5
                else:
                    score -= 0.5

            if action.action_name == "Steal":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for card in ["Captain", "Ambassador"]:
                        for i in range(2):
                            block_probability += self.card_probabilities[target['name']][card][i]
                    score -= block_probability * 2
                else:
                    score -= 0.5

            if score > best_score:
                best_target = target
                best_score = score

            target_scores[target['name']] = score

        return best_target, best_score

    def choose_influence_to_die(self):
        """
        Choose what influence to lose if the AI has more than one card.
        Otherwise, lose the remaining card.
        """
        if len(self.hand) == 1:
            return self.lose_card(0)

        card_scores = []
        for card in self.hand:
            card_scores.append(self.card_values[card.name])

        min_score_index = card_scores.index(min(card_scores))
        return self.lose_card(min_score_index)

    def select_exchange_cards(self, drawn_cards):
        """
        Choose what cards to keep from the exchange action.
        """
        combined_cards = self.hand + drawn_cards
        card_scores = []
        for card in combined_cards:
            card_scores.append(self.card_values[card.name])

        if len(drawn_cards) == 1:
            if card_scores[-1] > min(card_scores[:-1]):
                kept_cards = [combined_cards[-1]]
                removed_index = card_scores[:-1].index(min(card_scores[:-1]))
                for i in range(len(self.hand)):
                    if i != removed_index:
                        kept_cards.append(self.hand[i])
                self.hand = kept_cards
                returned_cards = [combined_cards[removed_index]]
            else:
                returned_cards = [combined_cards[-1]]
        else:
            sorted_indices = sorted(range(len(card_scores)), key=lambda i: card_scores[i], reverse=True)
            selected_indices = sorted_indices[:2]
            self.hand = []
            for i in selected_indices:
                self.hand.append(combined_cards[i])
            returned_cards = []
            for i, card in enumerate(combined_cards):
                if i not in selected_indices:
                    returned_cards.append(card)

        return returned_cards

    def prompt_show_card(self, card_name):
        """
        Show the card if the AI has it in the hand, otherwise don't show and lose the challenge.
        """
        if self.has_card(card_name):
            return True
        else:
            return False

    def prompt_challenge(self, action):
        """
        Prompt the AI to challenge the action based on the wants_to_challenge method.
        """
        return self.wants_to_challenge(action)

    def prompt_block(self, action):
        """
        Prompt the AI to block the action based on the wants_to_block method.
        """
        if self.wants_to_block(action):
            block_choice = self.get_block_choice(action.can_block)
            return block_choice
        else:
            return None

    def monte_carlo_simulation(self, game_state, action_log, num_simulations=1000):
        """
        Run Monte Carlo simulations to estimate the card probabilities.
        """
        simulated_probabilities = defaultdict(lambda: defaultdict(lambda: [0] * 2))

        for _ in range(num_simulations):
            simulated_state = self.simulate_game_state(game_state)
            simulated_action_log = self.simulate_action_log(action_log)
            updated_probabilities = self.update_probabilities_from_action_log(simulated_state, simulated_action_log)

            for player_name in updated_probabilities:
                for card_name in updated_probabilities[player_name]:
                    simulated_probabilities[player_name][card_name][0] += updated_probabilities[player_name][card_name][0]
                    simulated_probabilities[player_name][card_name][1] += updated_probabilities[player_name][card_name][1]

        for player_name in simulated_probabilities:
            for card_name in simulated_probabilities[player_name]:
                if num_simulations > 0:
                    simulated_probabilities[player_name][card_name][0] /= num_simulations
                    simulated_probabilities[player_name][card_name][1] /= num_simulations
                else:
                    simulated_probabilities[player_name][card_name] = [0, 0]

        return simulated_probabilities

    def simulate_game_state(self, game_state):
        """
        Simulate the game state by randomly distributing cards to opponents.
        """
        simulated_state = {
            "players": {},
            "all_lost_influences": game_state["all_lost_influences"][:],
        }

        remaining_cards = self.get_remaining_cards(game_state)
        random.shuffle(remaining_cards)

        for player_name, player_data in game_state["players"].items():
            if player_name != self.name:
                player_hand = remaining_cards[:2]
                remaining_cards = remaining_cards[2:]
                simulated_state["players"][player_name] = {
                    "hand": player_hand,
                    "coins": player_data["coins"],
                    "is_eliminated": player_data["is_eliminated"],
                    "influences_lost": player_data["influences_lost"][:],
                }
            else:
                simulated_state["players"][player_name] = {
                    "hand": [card.name for card in self.hand],
                    "coins": self.get_coins(),
                    "is_eliminated": self.is_eliminated,
                    "influences_lost": self.influences_lost[:],
                }

        return simulated_state

    def simulate_action_log(self, action_log):
        """
        Simulate the action log by copying relevant entries.
        """
        simulated_action_log = []
        for action in action_log:
            simulated_action = action.copy()
            if action["player"] != self.name:
                simulated_action["player"] = action["player"]
            if action["target"] is not None and action["target"] != self.name:
                simulated_action["target"] = action["target"]
            simulated_action_log.append(simulated_action)
        return simulated_action_log

    def update_probabilities_from_action_log(self, simulated_state, simulated_action_log):
        """
        Update the card probabilities based on the simulated action log.
        """
        updated_probabilities = defaultdict(lambda: defaultdict(lambda: [0] * 2))

        for action in simulated_action_log:
            player_name = action["player"]
            target_name = action["target"]
            action_name = action["action"]
            challenge = action["challenge"]
            challenge_outcome = action["challenge_outcome"]
            blocker = action["blocker"]
            blocker_claim = action["blocker_claim"]
            block_outcome = action["block_outcome"]
            card_shown = action["card_shown"]

            if action_name in ["Tax", "Assassinate", "Steal", "Exchange"]:
                if challenge is None and block_outcome is None:
                    updated_probabilities[player_name][action_name][0] += 1
                elif challenge is not None and challenge_outcome == "challenge_lost":
                    updated_probabilities[player_name][action_name][0] += 1
                    updated_probabilities[challenge][action_name][0] -= 1
                elif block_outcome == "block_failed":
                    updated_probabilities[player_name][action_name][0] += 1
                    updated_probabilities[blocker][blocker_claim][0] -= 1

            if card_shown is not None:
                updated_probabilities[player_name][card_shown][0] = 1
                updated_probabilities[player_name][card_shown][1] = 0

        return updated_probabilities

    def get_remaining_cards(self, game_state):
        """
        Get the remaining cards in the deck based on the current game state.
        """
        all_cards = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"] * 3
        for player_data in game_state["players"].values():
            if "hand" in player_data:
                for card in player_data["hand"]:
                    all_cards.remove(card)
        for card_name in game_state["all_lost_influences"]:
            all_cards.remove(card_name)
        return all_cards


class AIPlayerRuleBased(Player):
    """
    AIPlayerRuleBased is a rule-based AI player that uses predefined rules and strategies
    to make decisions in the game. It calculates probabilities for opponent cards and
    adjusts its card values based on the game state.
    """

    def __init__(self, name, game=None):
        """
        Initialize the AIPlayerRuleBased with the given name and game.
        """
        super().__init__(name)
        self.game = game
        self.card_probabilities = None  # Probabilities of opponent cards
        self.challenge_threshold = 2  # Round threshold for challenging
        self.card_values = {
            "Duke": 5,
            "Captain": 4,
            "Contessa": 3,
            "Assassin": 2,
            "Ambassador": 1
        }  # Card value mapping for decision-making
        self.last_actions = []

    def setup(self):
        """
        Setup the AIPlayerRuleBased by initializing the card probabilities.
        """
        self.initialize_card_probabilities()

    def reset(self):
        """
        Reset the AIPlayerRuleBased by resetting its parent class and re-initializing the card probabilities.
        """
        super().reset()
        self.initialize_card_probabilities()

    def is_human(self):
        """
        Indicate that this player is an AI player, not a human player.
        """
        return False

    def initialize_card_probabilities(self):
        """
        Initialize the card probabilities for all opponent players based on the current game state.
        """
        if self.game:
            game_state = self.game.get_game_state_for_ai(self)
            self.card_probabilities = self.calculate_probabilities(game_state)

    def calculate_probabilities(self, game_state):
        """
        Calculate the probabilities of opponent cards based on the current game state.
        """
        deck_probabilities = self.get_deck_probabilities(game_state)
        total_cards_in_deck = sum(deck_probabilities.values())
        probabilities = {}

        for player_name in game_state["players"]:
            if player_name != self.name:
                player_probabilities = {}
                for card_name in ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]:
                    player_probabilities[card_name] = [deck_probabilities[card_name] / total_cards_in_deck] * 2
                probabilities[player_name] = player_probabilities

        return probabilities

    def get_deck_probabilities(self, game_state):
        """
        Get the probabilities of cards remaining in the deck based on the current game state.
        """
        deck_probabilities = {
            "Duke": 3,
            "Assassin": 3,
            "Captain": 3,
            "Ambassador": 3,
            "Contessa": 3
        }

        # Subtract cards in the AI's hand from the deck probabilities
        for card in self.hand:
            deck_probabilities[card.name] -= 1

        # Subtract lost cards from the deck probabilities
        for card_name in game_state["all_lost_influences"]:
            deck_probabilities[card_name] -= 1

        print(deck_probabilities)
        return deck_probabilities

    def update_card_probabilities(self, player, action, game_state):
        """
        Update the card probabilities for the given player based on the performed action and game state.
        """
        if action.action_result == 'performed' and not action.challenge:
            card_name = action.required_card

            # Update the probability of the required card for the player
            for i in range(2):
                if self.card_probabilities[player.name][card_name][i] < 1:
                    self.card_probabilities[player.name][card_name][i] += 0.1
                    break

        if action.block_outcome == 'blocker not challenged' and not action.challenge:
            card_name = action.blocker_claim

            # Update the probability of the blocker's claimed card for the player
            for i in range(2):
                if self.card_probabilities[player.name][card_name][i] < 1:
                    self.card_probabilities[player.name][card_name][i] += 0.1
                    break

        if action.card_shown:
            card_name = action.card_shown
            deck_probabilities = self.get_deck_probabilities(game_state)
            deck_probabilities[card_name] += 1
            total_cards_in_deck = sum(deck_probabilities.values())

            # Update the probabilities for all cards based on the shown card
            for card in ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"]:
                for i in range(2):
                    self.card_probabilities[player.name][card][i] = deck_probabilities[card] / total_cards_in_deck

        # Normalize the probabilities for the player
        for player_name in self.card_probabilities:
            for card in self.card_probabilities[player_name]:
                total_probability = sum(self.card_probabilities[player_name][card])
                for i in range(2):
                    self.card_probabilities[player_name][card][i] /= total_probability

    def update_card_values_based_on_round(self):
        """
        Update the card values based on the current round and number of remaining players.
        """
        game_state = self.game.get_game_state_for_ai(self)

        if game_state["round"] >= 5 or len(game_state["players"]) <= 2:
            self.card_values = {
                "Captain": 5,
                "Assassin": 4,
                "Contessa": 3,
                "Duke": 5,
                "Ambassador": 1
            }

    def choose_action(self):
        self.update_card_values_based_on_round()
        game_state = self.game.get_game_state_for_ai(self)
        available_actions = self.get_available_actions(game_state)

        # Evaluate actions based on game state and probabilities
        action_scores = self.evaluate_actions(game_state, available_actions)

        # Check if the last 3 actions are the same
        if len(self.last_actions) >= 3 and len(set(self.last_actions[-3:])) == 1:
            # Choose the 2nd best action
            sorted_actions = sorted(available_actions, key=lambda action: action_scores[action.action_name], reverse=True)
            if len(sorted_actions) > 1:
                best_action = sorted_actions[1]
            else:
                best_action = sorted_actions[0]
        else:
            # Choose the action with the highest score
            best_action = max(available_actions, key=lambda action: action_scores.get(action.action_name, float('-inf')))

        if best_action.needs_target:
            best_target = self.choose_target(best_action)
            if best_target is None:
                available_actions.remove(best_action)
                if available_actions:
                    return self.choose_action()
                else:
                    return None
            best_action.target = best_target

        self.last_actions.append(best_action.action_name)
        return best_action

    def choose_target(self, action=None):
        """
        Choose the best target for the given action based on predefined rules.
        """
        game_state = self.game.get_game_state_for_ai(self)

        if action:
            available_targets = self.get_available_targets(game_state, action.action_name)
        else:
            available_targets = self.get_available_targets(game_state, None)

        if not available_targets:
            return None

        if action.action_name == "Coup":
            # If the AI player is forced to coup, select the best target for coup
            best_target, _ = self.evaluate_targets(game_state, action)
        else:
            best_target, _ = self.evaluate_targets(game_state, action)

        # Find the Player object corresponding to the best target
        for player in self.game.players:
            if player.name == best_target['name']:
                return player

        return None

    def wants_to_challenge(self, action, blocker=False):
        """
        Decide whether to challenge an action or a blocker's claim based on predefined rules.
        """
        game_state = self.game.get_game_state_for_ai(self)
        low_chance = 0.3  # Probability threshold below which AI will challenge

        if blocker:
            # In case of a block, 'action' contains the blocker's claim card
            action_name = action
            player = blocker.name
        else:
            # In other cases, 'action' is the actual Action object
            action_name = action.required_card
            player = action.player.name

        # If the AI has only one card left, it needs to be more cautious
        if len(self.hand) == 1:
            if action_name == "Assassin":
                # Special handling for assassination
                if not self.has_card("Contessa"):
                    if self.card_probabilities is not None:
                        return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
                    else:
                        return True  # Challenge if card_probabilities is None and AI has only one card left
            elif action_name == "Steal":
                # Special handling for steal
                if not (self.has_card("Ambassador") or self.has_card("Captain")):
                    if self.card_probabilities is not None:
                        return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
                    else:
                        return True  # Challenge if card_probabilities is None and AI has only one card left

        if game_state['round'] >= self.challenge_threshold:
            # General challenge logic for when AI has more than one card or for actions other than Assassin or Steal
            if self.card_probabilities is not None:
                return any(self.card_probabilities[player][action_name][i] < low_chance for i in range(2))
            else:
                return False  # Do not challenge if card_probabilities is None and AI has more than one card left

        return False

    def wants_to_block(self, action):
        """
        Decide whether to block an action based on predefined rules.
        """
        # First check if we have the blocking card.
        # Block if the AI has the blocking card
        for card_name in action.can_block:
            if self.has_card(card_name):
                return True

        # If the AI has 1 card left, it means that the probability of the player having the Assassinate card is high, so lie about blocking
        if len(self.hand) == 1:
            if action.action_name == "Assassinate":
                return True

        # For any other actions, for now, it's less risky to not block.

        return False

    def get_block_choice(self, block_options):
        """
        Get the required block card for the action, or choose a random card to bluff.
        """
        # Choose the blocking card if available
        for card_name in block_options:
            if self.has_card(card_name):
                return card_name

        # If no blocking card, choose a random card to lie
        return random.choice(block_options)

    def get_available_actions(self, game_state):
        """
        Get the available actions that the AI can perform based on the game state.
        """
        actions = [Income(self.game, self), ForeignAid(self.game, self), Tax(self.game, self), Exchange(self.game, self)]

        if self.get_coins() >= 3:
            if any(self.get_available_targets(game_state, "Assassinate")):  # Ensure there are targets
                actions.append(Assassinate(self.game, self, None))

        if self.get_coins() >= 7:
            if any(self.get_available_targets(game_state, "Coup")):  # Ensure there are targets
                actions.append(Coup(self.game, self, None))

        if any(self.get_available_targets(game_state, "Steal")):  # Ensure there are targets
            actions.append(Steal(self.game, self, None))

        return actions

    def get_available_targets(self, game_state, action_name, min_coins=0):
        """
        Get all valid targets for the chosen action based on the game state.
        """
        available_targets = []

        for player in game_state['players'].values():
            if player['name'] != self.name and not player['is_eliminated']:
                if action_name == "Steal" and player['coins'] < min_coins:
                    continue
                available_targets.append(player)

        return available_targets

    def evaluate_actions(self, game_state, actions):
        """
        Evaluate the available actions based on predefined rules and return a score for each action.
        """
        action_scores = {}

        for action in actions:
            score = 0

            # High priority action: Coup
            if action.action_name == "Coup":
                score += 5  # Assign a high score for Coup because it's a powerful move.

            # Tax action with possession of Duke
            if action.action_name == "Tax" and self.has_card("Duke"):
                score += 2  # Boost score if we have Duke, making Tax a strong option.

            # Actions requiring targets (Assassinate, Steal)
            if action.action_name in ["Assassinate", "Steal"]:
                best_target, target_score = self.evaluate_targets(game_state, action)
                if self.has_card(action.required_card):
                    score += target_score  # Add target evaluation score if we have the required card.
                else:
                    score -= 2  # Penalize the action if we don't have the required card.

            # Exchange action based on current card scores
            if action.action_name == "Exchange":
                card_score = sum(self.card_values[card.name] for card in self.hand)
                if card_score < 5:
                    score += 2  # Encourage Exchange if current cards are weak.

            # Basic actions with consistent benefit
            if action.action_name in ["Income", "Foreign Aid"]:
                score += 1  # Minor score boost for actions that generally succeed without challenge.

            action_scores[action.action_name] = score

        return action_scores

    def evaluate_targets(self, game_state, action):
        """
        Evaluate all the targets based on predefined rules and return the best target and its score.
        """
        target_scores = {}
        best_target = None
        best_score = float('-inf')

        for target in self.get_available_targets(game_state, action.action_name):
            score = 0
            player_data = game_state['players'][target['name']]

            if len(player_data['influences_lost']) == 1:
                score += 1
                score += player_data['coins'] / 10

            if action.action_name == "Coup":
                if len(player_data['influences_lost']) == 1:
                    score += player_data['coins'] / 5
                else:
                    score += player_data['coins'] / 10

            if action.action_name == "Assassinate":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for i in range(2):
                        block_probability += self.card_probabilities[target['name']]["Contessa"][i]
                    score -= block_probability * 2
                else:
                    score -= 0.5  # Assign a default penalty if card_probabilities is None

            if action.action_name == "Steal":
                if self.card_probabilities is not None:
                    block_probability = 0
                    for card in ["Captain", "Ambassador"]:
                        for i in range(2):
                            block_probability += self.card_probabilities[target['name']][card][i]
                    score -= block_probability * 2
                else:
                    score -= 0.5  # Assign a default penalty if card_probabilities is None

            if score > best_score:
                best_target = target
                best_score = score

            target_scores[target['name']] = score

        return best_target, best_score

    def choose_influence_to_die(self):
        """
        Choose what influence to lose if the AI has more than one card.
        Otherwise, lose the remaining card.
        """
        if len(self.hand) == 1:
            print(f"{self.name} is losing their last influence.")
            return self.lose_card(0)

        card_scores = [self.card_values[card.name] for card in self.hand]
        min_score_index = card_scores.index(min(card_scores))
        print(f"{self.name} is choosing to lose the {self.hand[min_score_index]} influence.")
        return self.lose_card(min_score_index)

    def select_exchange_cards(self, drawn_cards):
        """
        Choose what cards to keep from the exchange action.
        """
        combined_cards = self.hand + drawn_cards
        card_scores = []
        for card in combined_cards:
            card_scores.append(self.card_values[card.name])

        if len(drawn_cards) == 1:
            # If only one card is drawn, choose the best card to keep
            if card_scores[-1] > min(card_scores[:-1]):
                kept_cards = [combined_cards[-1]]
                removed_index = card_scores[:-1].index(min(card_scores[:-1]))
                for i in range(len(self.hand)):
                    if i != removed_index:
                        kept_cards.append(self.hand[i])
                self.hand = kept_cards
                returned_cards = [combined_cards[removed_index]]
            else:
                returned_cards = [combined_cards[-1]]
        else:
            # If two cards are drawn, choose the best two cards to keep
            sorted_indices = sorted(range(len(card_scores)), key=lambda i: card_scores[i], reverse=True)
            selected_indices = sorted_indices[:2]
            self.hand = []
            for i in selected_indices:
                self.hand.append(combined_cards[i])
            returned_cards = []
            for i, card in enumerate(combined_cards):
                if i not in selected_indices:
                    returned_cards.append(card)

        print(f"{self.name} is choosing to keep {[card.name for card in self.hand]} and return {[card.name for card in returned_cards]}.")
        return returned_cards

    def prompt_show_card(self, card_name):
        """
        Show the card if the AI has it in the hand, otherwise don't show and lose the challenge.
        """
        if self.has_card(card_name):
            print(f"{self.name} is showing the {card_name} card to win the challenge.")
            return True
        else:
            print(f"{self.name} does not have the {card_name} card and loses the challenge.")
            return False

    def prompt_challenge(self, action):
        """
        Prompt the AI to challenge the action based on the wants_to_challenge method.
        """
        if self.wants_to_challenge(action):
            print(f"{self.name} is challenging the {action.action_name} action.")
            return True
        else:
            print(f"{self.name} is not challenging the {action.action_name} action.")
            return False

    def prompt_block(self, action):
        """
        Prompt the AI to block the action based on the wants_to_block method.
        """
        if self.wants_to_block(action):
            block_choice = self.get_block_choice(action.can_block)
            print(f"{self.name} is blocking the {action.action_name} action with {block_choice}.")
            return block_choice
        else:
            print(f"{self.name} is not blocking the {action.action_name} action.")
            return None

    def get_remaining_cards(self, game_state):
        """
        Get the remaining cards in the deck based on the current game state.
        """
        # Initialize the list of all cards with three copies of each card
        all_cards = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"] * 3
        
        # Remove cards held by players from the deck
        for player_data in game_state["players"].values():
            if "hand" in player_data:
                for card in player_data["hand"]:
                    # Remove each card in the player's hand from the deck
                    if card in all_cards:
                        all_cards.remove(card)
        
        # Remove cards that have been lost from the deck
        remaining_cards = []
        for card in all_cards:
            # Check if the card is in the list of lost influences
            if card not in game_state["all_lost_influences"]:
                # If not, add it to the list of remaining cards
                remaining_cards.append(card)
        
        return remaining_cards
    
class RandomAIPlayer(Player):
    def __init__(self, name, game=None):
        super().__init__(name)
        self.game = game

    def setup(self):
        pass

    def is_human(self):
        """Differentiates between AI and Human players"""
        return False
 
    def choose_action(self):
        """Returns a valid random action"""
        available_actions = self.get_available_actions()
        if available_actions:
            chosen_action = random.choice(available_actions)
            if chosen_action.needs_target:
                chosen_target = self.choose_target(chosen_action)
                if chosen_target is None:
                    return self.choose_action()  # Retry choosing an action if no valid target is available
                chosen_action.target = chosen_target
            return chosen_action
        else:
            return Income(self.game, self)  # Choose Income action if no other actions are available


    def choose_target(self, action=None):
        """Returns a random valid target"""
        if action:
            available_targets = self.get_available_targets(action.action_name, min_coins=2 if action.action_name == "Steal" else 0)
        else:
            available_targets = self.get_available_targets(None)

        if available_targets:
            chosen_target = random.choice(available_targets)
            return chosen_target
        return None

    def get_available_actions(self):
        """Gets all the available actions the AI can perform"""
        actions = [Income(self.game, self), ForeignAid(self.game, self), Tax(self.game, self), Exchange(self.game, self)]
        if self.get_coins() >= 3 and any(self.get_available_targets("Assassinate")):
            actions.append(Assassinate(self.game, self, None))
        if self.get_coins() >= 7 and any(self.get_available_targets("Coup")):
            actions.append(Coup(self.game, self, None))
        if any(self.get_available_targets("Steal", min_coins=1)):
            actions.append(Steal(self.game, self, None))
        return actions

    def get_available_targets(self, action_name, min_coins=0):
        """Gets all the available targets"""
        return [player for player in self.game.players if player != self and not player.is_eliminated and player.coins >= min_coins]

    def wants_to_challenge(self, action, blocker=False):
        """Radomly decides to challenge"""
        return random.choice([True, False])

    def wants_to_block(self, action):
        """Radomly decides to block"""
        return random.choice([True, False])

    def get_block_choice(self, block_options):
        """Picks a random block card"""
        return random.choice(block_options)

    def choose_influence_to_die(self):
        """Chooses a random influence to die"""
        if self.hand:
            lost_card_index = random.choice(range(len(self.hand)))
            self.lose_card(lost_card_index)

    def lose_card(self, card_index):
        """Lose the required card"""
        if 0 <= card_index < len(self.hand):
            lost_card = self.hand.pop(card_index)
            self.influences_lost.append(lost_card.name)
            print(f"{self.name} has lost their {lost_card.name} influence.")
            if len(self.hand) == 0:
                self.set_eliminated(True)

    def select_exchange_cards(self, drawn_cards):
        """Randomly choose what two cards to keep"""
        total_cards = self.hand + drawn_cards
        if len(drawn_cards) == 1:
            # If only one card is drawn, randomly choose one card to keep
            to_keep = random.sample(total_cards, 1)
        else:
            # If two cards are drawn, randomly choose two cards to keep
            to_keep = random.sample(total_cards, 2)
        
        self.hand = to_keep
        return [card for card in total_cards if card not in to_keep]

    def prompt_show_card(self, card_name):
        """Shows the card if AI has it"""
        if self.has_card(card_name):
            return True
        else:
            return False
