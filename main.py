from src.wizard_logic import load_player_from_config, play_games, winning_probabilities


def main():
    """
    Main entry point for the Wizard game simulation via the Command Line Interface (CLI).

    This function handles the user input for player count, initializes the
    game environment, executes the simulation loop, and prints the final statistics.

    Args:
        None (Takes input from standard input/console).

    Returns:
        None.
    """
    print("===========================================")
    print("   WIZARD STRATEGY SIMULATION")
    print("===========================================\n")

    # 1. Configuration Setup
    full_playerlist = load_player_from_config()

    try:
        # Request user input for the number of participants
        n = int(input("How many players should participate? (3-6): "))
        if not (3 <= n <= 6):
            print("Invalid range. Defaulting to 3 players.")
            n = 3
    except ValueError:
        print("Invalid input. Defaulting to 3 players.")
        n = 3

    # 2. Simulation Setup
    playerlist = full_playerlist[:n]
    number_of_games = 1000

    print(f"Starting simulation with {n} players...")

    # Capture the return value of play_games
    simulation_winners = play_games(number_of_games, playerlist)

    # Pass the captured list to the statistics function
    stats = winning_probabilities(simulation_winners, number_of_games, playerlist)

    print("\nSimulation complete.")
    print(stats)


if __name__ == "__main__":
    main()