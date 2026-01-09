# 🧙 Wizard Strategy Simulation

This repository contains a Python-based **Monte Carlo Simulation** of the card game **Wizard**.
The primary objective is to investigate the statistical success and risks of an aggressive bidding and playing strategy compared to standard AI behaviors across different player counts (3-6 players).
Here you will find the rules of the game: https://blog.amigo-spiele.de/content/ap/rule/06900-GB-AmigoRule.pdf

---

## 📂 Project Structure

Following the organizational standards for data science projects, the repository is structured as follows:

```text
wizard-simulation/
├── configs/            # Configuration files
│   └── players.json    # Player profiles and playing styles
├── data/               # Raw and processed simulation data
├── notebooks/          # Data exploration and visualization
│   └── wizard_analysis.ipynb  # Main analysis notebook
├── reports/            # Generated output
│   ├── figures/        # Exported plots (PNG/PDF)
│   └── last_simulation.csv # Simulation results with metadata
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

    Command Line Interface: Run a quick simulation with user-defined player counts.
    Bash

python main.py

Jupyter Notebook: For a detailed graphical analysis and win-rate comparison, open the notebook:
Bash

    jupyter notebook notebooks/wizard_analysis.ipynb

🔬 Methodology & Reproducibility

    Aggressive AI: The strategy (Player: "Testo_Torsten") implements a bidding bias (+0.7 on predicted tricks) and an offensive trick-taking logic.

    Separation of Concerns: Business logic is strictly kept within the src/ modules, while the notebooks/ are used solely for presentation and visualization.

    Consistency: A fixed random seed (42) is utilized across all modules to ensure that simulation results are 100% reproducible.

👥 Contributors

    Team Member 1 - [Janis Müller]

    Team Member 2 - [Phillip Engel]