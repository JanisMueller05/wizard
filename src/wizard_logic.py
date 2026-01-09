from src.card import Card
from src.player import Player
import json
import numpy as np
import pandas as pd
import datetime
import math
import os

# Prevent columns from being abbreviated with "..." (AI)
pd.set_option('display.max_columns', None)
# Allow a very wide display in the terminal (AI)
pd.set_option('display.width', 5000)
# Center the headers over the data (AI)
pd.set_option('display.colheader_justify', 'center')


rng = np.random.default_rng(seed=42)  # Random number generator with seed

colors = ["red", "green", "blue", "yellow"]


def load_player_from_config():
    """
    Loads player configurations from a JSON file and initializes Player objects.
    """
    #AI
    # Open the passive text file
    with open("configs/players.json", "r", encoding="utf-8") as f:
        data = json.load(f)  # Macht aus dem Text ein Dictionary

    # Build actual Python objects from the data
    player_objects = []
    for s in data["player"]:
        # Instantiate the Player class
        new_player = Player(s["name"], 0, [], playing_style=s["playing_style"])
        player_objects.append(new_player)

    return player_objects



def shuffle_cards():
    """
    Generates a full Wizard deck including Wizards and Jesters, then shuffles it.
    """
    cards = []
    for color in colors:
        cards.append(Card("", 14))   # wizard
        cards.append(Card("", 0))    # jester
        for value in range(13):
            cards.append(Card(color, value + 1))
    rng.shuffle(cards)
    return cards


def number_of_rounds_to_be_played(number_of_players):
    """
    Calculates the total number of rounds based on the number of players.

    Args:
        number_of_playerss (int): The total number of people participating in the game.
    """
    return 60 // number_of_players


def create_points_table(player_names: list[str]) -> pd.DataFrame:
    """
    Creates an empty Pandas DataFrame for the points table with MultiIndex columns.

    Args:
        player_names (list[str]): A list of player names to be used as the top-level column index.
    """
    #AI
    # Create a MultiIndex (Hierarchical index) for columns: Player -> Category
    columns = pd.MultiIndex.from_product([player_names, ["announced_tricks", "tricks_made", "points"]],
                                         names=['player', 'category'])
    points_table = pd.DataFrame(columns=columns)
    points_table.index.name = 'round'
    # Explicit type conversion to avoid NaN issues
    return points_table.astype('int64')


def add_points(points_table: pd.DataFrame, round_number: int,
               round_data: dict[str, list[int]]) -> pd.DataFrame:
    """
    Adds the results of a specific game round to the points table.

    Args:
        points_table (pd.DataFrame): The current DataFrame holding all game scores.
        round_number (int): The index (row) where the data should be inserted.
        round_data (dict): A dictionary where keys are player names and values
                           are lists containing [bidded, made, points].
    """
    #AI
    new_round = {}
    for player, data in round_data.items():
        new_round[(player, 'announced_tricks')] = data[0]
        new_round[(player, "tricks_made")] = data[1]
        new_round[(player, 'points')] = data[2]
    points_table.loc[round_number] = new_round
    return points_table


def calculate_total_points(table: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a row ‘total’ containing the sum of all ‘points’ for each player.

    Args:
        table (pd.DataFrame): The complete points table after all rounds are played.
    """
    #AI
    # Extract only the 'points' columns and sum them vertically
    total_points_row = table.xs('points', level='category', axis=1).sum(axis=0)
    total_row = {}
    for player in table.columns.get_level_values('player').unique():
        # Reset trick counts for the total row and set the calculated sum
        total_row[(player, 'announced_tricks')] = 0
        total_row[(player, "tricks_made")] = 0
        total_row[(player, 'points')] = total_points_row[player]
    table.loc['total'] = total_row
    return table, total_points_row



def winner_of_the_game(total_row):
    """
    Identifies all players with the highest total points to handle ties correctly.

    Args:
        total_row (pd.Series): A Series containing the final point totals for each player.

    Returns:
        tuple[list[str], int]: A list of winner names and the maximum score achieved.
    """
    # Find the maximum score achieved in the game
    max_points = total_row.max()

    # Identify all players who reached this maximum score (handling draws)
    winners = total_row[total_row == max_points].index.tolist()

    return winners, max_points


def print_table(table: pd.DataFrame):
    """
    Prints the Pandas points table in a readable format to the console.

    Args:
        table (pd.DataFrame): The DataFrame to be displayed.
    """
    #print(table.to_string())



def play_round(current_round, trump_color, table, number_of_rounds, playerlist):
    """
    Executes a full round of the game.

    Args:
        current_round (int): The number of the current round being played.
        trump_color (str): The color that is trump for this round.
        table (pd.DataFrame): The current points table to be updated.
        number_of_rounds (int): The total number of rounds in the game.
        playerlist (list): A list of Player objects participating in the round.

    Returns:
        pd.DataFrame: The updated points table after the round ends.
    """

    round_data = {}

    #Bidding Phase
    for player in playerlist:
        #print("-----")
        #print(f"player: {player.name}")

        #print(f"cards on hand ({len(player.cards_in_hand)}): {player.cards_in_hand}")
        #print("-----")


        number_of_announced_tricks = evaluate_cards(player.cards_in_hand, trump_color, playerlist, current_round, player.playing_style)
        #print(f" -> number of announced tricks: {number_of_announced_tricks}")

        round_data[player.name] = [
            number_of_announced_tricks, 0, 0
        ]
        # Preliminary save of bids so play_trick can access them
        table = add_points(table, current_round, round_data)


    trick_winner = []

    number_of_tricks_in_round = {player.name: 0 for player in playerlist}

    # Calculate who starts the round.
    starting_player_index = (current_round % len(playerlist)) - 1

    for i in range(current_round):
        # Play individual trick
        winner = play_trick(playerlist, starting_player_index, trump_color, current_round, table, number_of_tricks_in_round)

        trick_winner.append(winner)
        number_of_tricks_in_round[winner] += 1

        # Winner of the last trick starts the next one
        trick_winner_last_round = next(                                      #AI
            (player for player in playerlist if player.name == winner))
        starting_player_index = playerlist.index(trick_winner_last_round)


    for player in playerlist:
        # Evaluate how many tricks were actually made vs announced
        number_of_tricks_made = number_of_made_tricks(player, trick_winner)
        number_of_announced_tricks_alt = round_data[player.name][0]
        round_data[player.name] = [number_of_announced_tricks_alt, number_of_tricks_made, 0]

    # Calculate and save points
    for player, data in round_data.items():
        number_of_announced_tricks = data[0]
        number_of_tricks_made = data[1]

        # Scoring logic: 20 base points + 10 per trick if correct, else -10 per difference
        if number_of_announced_tricks == number_of_tricks_made:
            points = 20 + number_of_tricks_made * 10
        else:
            points = (abs(number_of_announced_tricks - number_of_tricks_made)) * (-10)

        round_data[player] = [number_of_announced_tricks, number_of_tricks_made, points]

    # Fill table and output results
    table = add_points(table, current_round, round_data)
    table = table.fillna(0).astype(int)

    # Add total sum if it was the final round
    if current_round == number_of_rounds:
        table, total_points = calculate_total_points(table)
        #print("\n FInAL SCORE OF THE GAME (incl. total) ")
        print_table(table)
        winner, points = winner_of_the_game(total_points)
        #print(f" -> winner is: {winner} with {points} points.")
    #else:
        #print("\n-----------")
        #print(f"RESULTS AFTER ROUND {current_round}")
        #print("-----------")
        #print_table(table)

    return table


def start_game(starting_round, playerlist):
    """
    Main loop to control the Wizard game from a specific starting round to the end.

    Args:
        starting_round (int): The round number to begin with (usually 1).
        playerlist (list): A list of Player objects participating in the game.
    """
    # Calculate the total number of rounds based on player count
    round_number = number_of_rounds_to_be_played(len(playerlist))
    player_names_str = [player.name for player in playerlist]

    # Initialize the score tracking table
    table = create_points_table(player_names_str)

    #print("\n===========================================")
    #print(f" START WIZARD GAME WITH {round_number} rounds")
    #print("===========================================")

    for current_round in range(starting_round, round_number + 1):
        #print(f"\n====================== round {current_round} ======================")

        # Prepare the deck for the new round
        cards = shuffle_cards()

        # Deal cards to players and determine trump color
        remaining_cards = distribute_cards(cards, current_round, playerlist)
        trump_color = choose_trump(remaining_cards, current_round, playerlist)

        #print(f" starting player: {playerlist[current_round % len(playerlist) - 1]}")
        #print(f" Trumpcolor: {trump_color} | {current_round} cards per player")

        # Execute the trick-taking phase and update scores
        table = play_round(current_round, trump_color, table, round_number, playerlist)

    # Calculate total points after all rounds are finished
    # We use cross-section 'xs' to get the 'points' columns
    total_points_series = table.xs('points', level='category', axis=1).sum(axis=0)

    # Capture winners from the calculation function
    winners, max_score = winner_of_the_game(total_points_series)

    return winners, max_score




def distribute_cards(cards, number_of_cards, playerlist):
    """
    Distributes the specified number of cards to each player from the deck.

    Args:
        cards (list): The list of Card objects currently in the deck.
        number_of_cards (int): How many cards each player should receive this round.
        playerlist (list): The list of Player objects receiving the cards.

    Returns:
        list: The remaining cards in the deck after distribution.
    """

    for i in range(number_of_cards):
        for player in playerlist:
            top_card = cards.pop(0)
            player.cards_in_hand.append(top_card)

    return cards

def choose_trump(remaining_cards, current_round, playerlist):
    """
    Determines the trump color for the current round based on the deck's top card.

    Args:
        remaining_cards (list): The cards left in the deck after dealing.
        current_round (int): The current round number (used to find the starting player).
        playerlist (list): The list of players in the game.

    Returns:
        str or None: The trump color (e.g., 'red', 'blue'), or None if no trump exists.
    """
    if remaining_cards:
        trump_card = remaining_cards[0]  # Reveal top card
    else:
        return None

    if trump_card.color in colors:
        trump_color = trump_card.color
    # Jester case: No trump color for this round
    elif trump_card.value == 0:
        trump_color = None
    # Wizard case: The starting player chooses the trump suit
    elif trump_card.value == 14:
        frequencies = {color: 0 for color in colors}       #AI
        # Identify the player who gets to choose
        starting_player = playerlist[(current_round % len(playerlist)) - 1]

        # Analyze the player's hand to make a strategic choice.
        for card in starting_player.cards_in_hand:
            color = card.color
            if color in colors:
               frequencies[color] = frequencies.get(color,0) + 1   #AI

        # Fallback: If no standard colors are in hand (only Wizards/Jesters)
        if all(count == 0 for count in frequencies.values()):
            # Select a random color to avoid logic errors
            trump_color = rng.choice(colors)

        # Logic for choosing the replacement trump suit based on playing style
        elif starting_player.playing_style == "aggressive":
            # Aggressive players choose their most frequent color
            trump_color = max(frequencies, key=frequencies.get)   #AI

            # Select color with lowest frequency for a defensive approach
        else: trump_color = min(frequencies, key=frequencies.get) #AI

    return trump_color


def evaluate_cards(cards, trump_color, playerlist, current_round, playing_style):
    """
    Estimates the number of tricks a player is likely to win based on their hand.

    Args:
        cards (list): List of Card objects in the player's hand.
        trump_color (str or None): The color that is trump for this round.
        playerlist (list): List of all players (used to determine player count).
        current_round (int): The current round number
        playing_style (str): The AI style ("aggressive" or "normal").

    Returns:
        int: The predicted number of tricks (bidded tricks).
    """
    number_of_players = len(playerlist)
    #AI
    total_prob = 0

    for card in cards:
        prob = 0  # Probability of this specific card winning a trick

        # Wizards (Value 14) are highly likely to win
        if card.value == 14:
            prob = 0.95

        # Jesters (Value 0) are very unlikely to win
        elif card.value == 0:
            prob = 0.05

        # Trump cards
        elif card.color == trump_color:
            # Value relative to the highest possible card (13)
            prob = (card.value / 13) * 0.8

            # In early rounds, trump cards are more powerful
            if current_round < 5:
                prob += 0.1
            if card.value > 10: prob += 0.15

        # Standard color cards
        else:
            # Probability decreases as the number of players increases (risk of being trumped)
            basis_prob = (card.value / 13)
            # Risk scaling: chance of a normal card winning drops with more opponents
            player_malus = 0.75 ** (number_of_players - 1)
            prob = basis_prob * player_malus

            # Low cards become less valuable in later rounds with more cards in play
            if current_round > 5 and card.value < 8:
                prob *= 0.5

        total_prob += prob



    # Special case: In round 1, ensure a bid of 1 if the card is strong enough
    if current_round == 1 and total_prob > 0.4:
        return 1

    # Apply personality-based bidding
    if playing_style == "aggressive":
        # Aggressive players round up more easily (biased towards higher bids)
        number_of_tricks = math.floor(total_prob + 0.7)
    else:
        # Basic rounding
        number_of_tricks = round(total_prob)

    # Cannot bid more tricks than cards held
    return min(number_of_tricks, len(cards))


def play_trick(playerlist, starting_player_index, trump_color, current_round, table, number_of_tricks_in_round):
    """
    Simulates a single trick where every player plays one card.

    Args:
        playerlist (list): List of all Player objects.
        starting_player_index (int): Index of the player who leads the trick.
        trump_color (str or None): The current trump color.
        current_round (int): The current round number.
        table (pd.DataFrame): The points table (used to check bids).
        number_of_tricks_in_round (dict): Track of how many tricks each player has already won.

    Returns:
        str: The name of the player who won the trick.
    """
    trick_cards = {}
    operating_color = ""
    current_winning_card = None
    winner = None

    for i in range(len(playerlist)):
        # Determine who is the current active player (handling turn rotation)
        active_player = playerlist[(starting_player_index + i) % len(playerlist)]
        #print(active_player)

        # Retrieve bid data from the table
        planned_tricks = table.loc[current_round, (active_player.name, 'announced_tricks')]

        # Track won tricks locally to decide strategy
        current_made_tricks = number_of_tricks_in_round[active_player.name]

        # Strategic decision: Does the player want to win this trick?
        wants_trick = current_made_tricks < planned_tricks

        # Find all valid moves based on Wizard rules
        possible_cards = permitted_cards_for_move(active_player.cards_in_hand, operating_color)

        # Select the best card to play based on strategy and game state
        played_card = (choose_smart_card
                         (possible_cards,
                          current_winning_card,
                          trick_cards,
                          operating_color,
                          trump_color,
                          playerlist,
                          wants_trick,
                          playing_style=active_player.playing_style))

        # Set the led color (operating color) if it hasn't been set yet
        if operating_color == "" and played_card.color != "":
            operating_color = played_card.color

        # Evaluate if the newly played card takes the lead
        if current_winning_card is None or is_stronger(played_card, current_winning_card, operating_color, trump_color):
            current_winning_card = played_card
            winner = active_player.name

        # Remove card from hand and record it in the current tric
        active_player.cards_in_hand.remove(played_card)
        trick_cards[active_player.name] = played_card



    #print(f"The trick: {trick_cards}")
    #print(f"winner of the trick is: {winner} with {current_winning_card}")

    return winner


def choose_smart_card(cards, highest_trick_card, trick_cards, operating_color, trump_color, playerlist, wants_trick=True, playing_style="normal"):
    """
    Decides which card to play based on the current trick state and player strategy.

    Args:
        cards (list): Valid cards available in the player's hand.
        highest_trick_card (Card or None): The card currently leading the trick.
        trick_cards (dict): Dictionary of cards already played in this trick {player_name: Card}.
        operating_color (str): The color that must be followed (led color).
        trump_color (str or None): The trump color for the round.
        playerlist (list): List of all players.
        wants_trick (bool): Strategy flag; True if the player aims to win the trick.
        playing_style (str): The AI personality ("aggressive" or "normal").

    Returns:
        Card: The strategically chosen card to play.
    """
    #AI
    winner_cards = []
    loser_cards = []

    # 1. Categorize cards into those that can win the trick and those that cannot
    for card in cards:
        # If the trick is empty, any card except a Jester is a potential winner
        if highest_trick_card is None:
            if card.value > 0:
                winner_cards.append(card)
            else:
                loser_cards.append(card)
        # Check against the currently leading card
        elif is_stronger(card, highest_trick_card, operating_color, trump_color):
            winner_cards.append(card)
        else:
            loser_cards.append(card)

    # 2. Apply Strategy
    if wants_trick:
        if winner_cards:
            if playing_style == "aggressive":
                # AGGRESSIVE: If leading, prefer playing a high trump card
                if not trick_cards:
                    trump_cards = [card for card in winner_cards if card.color == trump_color]
                    if trump_cards:
                        return max(trump_cards, key=lambda card: card.value)
                # Otherwise, play the HIGHEST winning card to secure the trick
                return max(winner_cards, key=lambda card: card.value)
            else:
                # NORMAL: Play the lowest possible winning card (efficiency)
                return min(winner_cards, key=lambda card: card.value)
        else:
            # Cannot win: Discard a low card (preferably not a trump or special card)
            normal_color_cards = [card for card in loser_cards if
                                  card.color != trump_color and card.value not in [0, 14]]
            if normal_color_cards:
                return min(normal_color_cards, key=lambda card: card.value)
            return min(cards, key=lambda card: card.value)

    else:
        # Strategy: Does NOT want the trick
        if loser_cards:
            # Get rid of Wizards if they won't win (e.g., if a Wizard was already played)
            wizards = [card for card in loser_cards if card.value == 14]
            if wizards:
                return wizards[0]

            trump_cards = [card for card in loser_cards if card.color == trump_color]
            if trump_cards:
                # Discard the highest trump card that currently doesn't win
                return max(trump_cards, key=lambda card: card.value)

            # Otherwise, discard the highest losing card
            return max(loser_cards, key=lambda card: card.value)
        else:
            # Forced to win? Check if opponents are still to play
            number_of_cards_in_trick = len(trick_cards)
            still_players_left = number_of_cards_in_trick < (len(playerlist) - 1)

            if still_players_left:
                # Play low and hope someone else takes the trick
                return min(cards, key=lambda card: card.value)
            else:
                # Last player and must win: Play the highest card to "clear" it
                return max(cards, key=lambda card: card.value)


def is_stronger(new_card, best_card_so_far, operating_color, trump_color):
    """
    Compares two cards to determine if the new card beats the current leader.
    Implements official Wizard rules.

    Args:
        new_card (Card): The card being played.
        best_card_so_far (Card): The card currently winning the trick.
        operating_color (str): The color led in this trick.
        trump_color (str or None): The trump color for the round.

    Returns:
        bool: True if the new_card wins against the best_card_so_far.
    """
    # 1. Wizard Rule: The first Wizard played in a trick always wins.
    if best_card_so_far.value == 14:
        return False

    if new_card.value == 14:
        return True

    # 2. Jester Rule: A Jester (0) never beats a card already leading.
    if new_card.value == 0:
        return False

    # 3. Trump Logic
    # New card is trump, current leader is not
    if new_card.color == trump_color and best_card_so_far.color != trump_color:
        return True
    # Both are trump: Higher value wins
    if new_card.color == trump_color and best_card_so_far.color == trump_color:
        return new_card.value > best_card_so_far.value

    # 4. Led Color (Operating Color) Logic
    # New card follows suit, leader is neither trump nor led color
    if new_card.color == operating_color and best_card_so_far.color != operating_color:
        return True
    # Both follow suit: Higher value wins
    if new_card.color == operating_color and best_card_so_far.color == operating_color:
        return new_card.value > best_card_so_far.value

    # 5. Default: Discards or lower values do not win
    return False






def permitted_cards_for_move(cards, operating_color):
    """
    Determines which cards are legally playable according to Wizard rules

    Args:
        cards (list): The cards currently in the player's hand.
        operating_color (str): The suit that was led in the current trick.

    Returns:
        list: All cards that are allowed to be played.
    """
    # If no color has been led yet, all cards in hand are valid
    if not operating_color:
        return cards

    # Check if the player has any cards of the led suit.
    operating_color_cards = [card for card in cards if card.color == operating_color]

    # If the player cannot follow suit, they can play any card (discarding or trumping)
    if not operating_color_cards:
        return cards

    # If they can follow suit, they must play either the suit or a special card
    # Special cards are identified by having an  empty color string ""
    permitted_cards = [card for card in cards if card.color == operating_color or card.color == ""]
    return permitted_cards



def number_of_made_tricks(player, trick_winner):
    """
    Counts how many tricks a specific player won in a round.

    Args:
        player (Player): The player object to check.
        trick_winner (list): A list of names of the winners for each trick in the round.

    Returns:
        int: Total number of tricks won by the player.
    """
    number_of_tricks_made = trick_winner.count(player.name)
    return number_of_tricks_made




def play_games(number_of_games, playerlist):
    """
    Runs a simulation of multiple complete Wizard games.

    Args:
        number_of_games (int): Total number of games to simulate.
        playerlist (list): List of Player objects.

    Returns:
        list[str]: A list containing the names of the winners of each game.
    """
    all_winners_collected = []

    for i in range(number_of_games):
        # We capture the winners returned by each individual game
        winners, _ = start_game(1, playerlist)
        # Add all winners (handles ties) to the overall result list
        all_winners_collected.extend(winners)

    return all_winners_collected




def winning_probabilities(winner_data_list, number_of_games, playerlist):
    """
    Calculates the win rate for each player and exports the results.

    Args:
        winner_data_list (list): The list of winner names from play_games.
        number_of_games (int): Total number of games played.
        playerlist (list): List of all participating players.

    Returns:
        pd.DataFrame: A DataFrame showing win rates as formatted percentages.
    """

    probabilities = {
        player.name: winner_data_list.count(player.name) / number_of_games
        for player in playerlist
    }

    df = pd.DataFrame(probabilities, index=["winningchance"])

    # Convert values to formatted percentage strings for console display
    df_percent= df.map(lambda x: f"{x * 100:.1f}%")

    # Export results to CSV with simulation metadata.
    export_with_metadata(df_percent, "last_simulation", seed=42)

    return df_percent



def export_with_metadata(df, filename, seed=42):
    """
    Saves a DataFrame to a CSV file in the 'reports' folder with a custom metadata header.

    Args:
        df (pd.DataFrame): The data to be saved.
        filename (str): The desired filename (without extension).
        seed (int): The random seed used for the simulation to ensure reproducibility.
    """
    # Create the reports directory if it does not exist
    os.makedirs("reports", exist_ok=True) #erstelltOrdner reports falls er fehlt

    # Creates the fitting timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct header lines with '#' prefix
    header = [
        f"# Project: Wizard Simulation",
        f"# Creation Dte: {timestamp}",
        f"# Used Seed: {seed}",
        f"# Status: Final Result",
        "#"
    ]

    path = f"reports/{filename}.csv"

    # Write the header first, then append the DataFrame as CSV
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(header) + "\n")
        df.to_csv(f, index=True)

    print(f" Results successfully saved under: {path}")


def run_full_simulation(min_players=3, max_players=6, games_per_round=1000):
    """
    High-level function to run multiple scenarios for the Notebook analysis.

    Args:
        min_players (int): Starting number of players (default: 3).
        max_players (int): Ending number of players (default: 6).
        games_per_round (int): Simulation scale (default: 1000).

    Returns:
        pd.DataFrame: A structured DataFrame for plotting win rates.
    """
    results_data = []
    full_player_pool = load_player_from_config()

    for n in range(min_players, max_players + 1):
        active_players = full_player_pool[:n]

        # Capture return value from simulation
        winners_list = play_games(games_per_round, active_players)

        for player in active_players:
            win_count = winners_list.count(player.name)
            results_data.append({
                "PlayerCount": n,
                "Player": player.name,
                "Winrate": (win_count / games_per_round) * 100
            })

    return pd.DataFrame(results_data)