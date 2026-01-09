🧙 Wizard Strategy Simulation

Project Organization

Course: Simulations Tools WI25/26
Date: 9.01.2026
Authors: Janis Müller, Phillip Engel


This repository contains a Python-based Monte Carlo Simulation of the card game Wizard. The primary objective is to investigate the statistical success and risks of an aggressive bidding and playing strategy compared to standard AI behaviors across different player counts (3–6 players).

Official game rules can be found here: Amigo Wizard Rules
📂 Project Structure

Following the organizational standards for data science projects, the repository is structured as follows:
Plaintext

wizard-simulation/
├── configs/            # Configuration files (JSON player profiles)
├── notebooks/          # Data exploration and visualization
│   └── wizard_analysis.ipynb  # Main analysis notebook
├── reports/            # Generated output (Plots & CSV)
├── src/                # Core logic (Production Code)
│   ├── card.py         # Card class and logic
│   ├── player.py       # Player class and strategy handling
│   └── wizard_logic.py # Game engine and simulation suite
├── main.py             # CLI Entry point
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation

🚀 Getting Started
1. Installation

This project requires Python 3.8+. Clone the repository and install the necessary libraries:
Bash

pip install -r requirements.txt

(Key libraries: numpy, pandas, matplotlib, seaborn)
2. Running the Simulation

You can interact with the project in two ways:

    Command Line Interface (CLI): Run a quick simulation with user-defined player counts to see immediate results in the terminal.
    Bash

python main.py

Jupyter Notebook: For a detailed graphical analysis, win-rate comparisons, and trend visualizations across all player counts:
Bash

    jupyter notebook notebooks/wizard_analysis.ipynb

🔬 Methodology & Reproducibility

    Aggressive AI Strategy: The "Aggressive" profile (Player: Testo_Torsten) is characterized by:

        Bidding Bias: A systematic overestimation of hand strength (+0.7 bias on predicted tricks).

        Offensive Lead: Playing high trump cards early to "bleed" opponents' resources.

        Strategic Trump Choice: Maximizing suit frequency when choosing the trump color via a Wizard card.

    The "Positioning Effect": Our analysis identified that players following the aggressive actor (e.g., Gregor_Samsa) often experience a significant "boost" in win rates (up to 49% in 3-player games), as they can exploit the resource depletion caused by the aggressor.

    Scale & Skalability: We use a Monte Carlo approach with 1,000 games per scenario to ensure results are statistically significant. The simulation clearly shows that aggressive strategies collapse as the player count increases due to higher trick-competition.

    Separation of Concerns: Business logic is strictly encapsulated within the src/ modules, while the notebooks/ are used solely for presentation and visualization.

    Consistency: A fixed random seed (42) is utilized across all modules to ensure that all results are 100% reproducible.
