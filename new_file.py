import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PLAYERS = ["Silas", "Lage", "Zeno", "Josie", "Miriam", "Felipe", "John", "Vilmos", "William", "Lilly", "Elsa", "Lukas", "Guest", "Angelina", "Hedvig", "Anni", "Yves"]

LUCK = {
    "Terraforming Mars": 0.85,
    "Great Western Trail": 0.9,
    "GWT New Zealand": 0.9,
    "Wingspan": 0.75,
    "Root": 0.8,
    "Shogun": 0.7,
    "Parks": 0.7,
    "Terraforming Mars: The Dice Game": 0.55,
    "Flamme Rouge": 0.75,
    "Quacks of Quedlingburg": 0.4,
    "Treasure Island": 0.65,
    "Bohnanza": 0.6,
    "6 Nimmt": 0.55,
    "Dominion": 0.7,
    "7 Wonders": 0.7,
    "Galaxy Trucker": 0.6,
    "Durak": 0.65,
    "For Sale": 0.6,
    "Wizard": 0.65,
    "Scout": 0.6,
    "Coup": 0.65,
    "Ya Blew It": 0.45,
    "Railroad Ink": 0.55,
    "Cabanga" : 0.5,
    "Innovation": 0.55
}

def read():
    return pd.read_csv("KTK Board Games - Speldata.csv")

def partition(df):
    groups_map = {
        "Stora spel": ["Terraforming Mars", "Great Western Trail", "GWT New Zealand", "Wingspan", "Root", "Shogun"],
        "Medel spel": ["Parks", "Terraforming Mars: The Dice Game", "Flamme Rouge",
                    "Quacks of Quedlingburg", "Treasure Island", "Bohnanza",
                    "6 Nimmt", "Dominion", "7 Wonders", "Galaxy Trucker", "Captain Sonar", "Innovation"],
        "Små spel": ["Durak", "For Sale", "Wizard", "Scout", "Coup", "Ya Blew It", "Railroad Ink", "Cabanga"],
    }
    return {name: df[df["Spel"].isin(keywords)] for name, keywords in groups_map.items()}

def parse_ties(annotation):
    if pd.isna(annotation):
        return {}
    ties = {}
    for group in annotation.split("|"):
        group = group.strip()
        place, players = group.split(":")
        ties[int(place.strip()[1:])] = [p.strip() for p in players.split(",")]
    return ties

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_a, rating_b, score_a, k):
    return rating_a + k * (score_a - expected_score(rating_a, rating_b))

def process_game(ratings, ranking, k, ties={}):
    new_ratings = ratings.copy()
    place_of = {player: i + 1 for i, player in enumerate(ranking)}
    for place, tied_players in ties.items():
        for player in tied_players:
            place_of[player] = place
    for i in range(len(ranking)):
        for j in range(i + 1, len(ranking)):
            winner, loser = ranking[i], ranking[j]
            score = 0.5 if place_of[winner] == place_of[loser] else 1.0
            new_ratings[winner] = update_elo(new_ratings[winner], new_ratings[loser], score, k)
            new_ratings[loser] = update_elo(new_ratings[loser], new_ratings[winner], 1 - score, k)
    return new_ratings

def analyze(groups):
    mega_results = {}
    total_points = {player: np.array([0.0, 0.0]) for player in PLAYERS}

    for name, group in groups.items():
        points = {player: np.array([0.0, 0.0]) for player in PLAYERS}
        for index, row in group.iterrows():
            ties = parse_ties(row["Ties"])
            
            # Build a place lookup, averaging tied places
            tie_scores = {}
            for place, tied_players in ties.items():
                num_tied = len(tied_players)
                for player in tied_players:
                    tie_scores[player] = (place, num_tied)

            if row["Speltyp"] == "Rankning":
                num_p = float(row["Antal Spelare"])
                for kolumn in range(1, 9):
                    if pd.notna(row[f"Kolumn {kolumn}"]):
                        player = row[f"Kolumn {kolumn}"]
                        if player in tie_scores:
                            place, num_tied = tie_scores[player]
                            # Average the scores of all tied places
                            avg_score = sum(1 - (p - 1) / (num_p - 1) for p in range(place, place + num_tied)) / num_tied
                        else:
                            avg_score = 1 - (kolumn - 1) / (num_p - 1)
                        points[player] += np.array([avg_score, 1.0])

            elif row["Speltyp"] == "En vinnare":
                num_p = float(row["Antal Spelare"])
                non_winner_score = (num_p**2 - 3*num_p + 2) / (2*(num_p - 1)**2)
                for kolumn in range(1, 9):
                    if pd.notna(row[f"Kolumn {kolumn}"]):
                        player = row[f"Kolumn {kolumn}"]
                        avg_score = 1.0 if kolumn == 1 and player not in tie_scores else non_winner_score
                        points[player] += np.array([avg_score, 1.0])

        results = {key: (round(value[0]/value[1], 2), int(value[1])) for key, value in points.items()}
        mega_results[name] = results
        for key, value in points.items():
            total_points[key] += value

    mega_results["Totalt"] = {key: (round(value[0]/value[1], 2), int(value[1])) for key, value in total_points.items()}
    return pd.DataFrame(mega_results)

def calculate_elo(groups, k=32, use_luck = True):
    ratings = {player: 1000 for player in PLAYERS}
    all_games = pd.concat(groups.values()).sort_values("Datum")
    for index, row in all_games.iterrows():
        if row["Speltyp"] in ["Rankning", "En vinnare"]:
            ranking = [row[f"Kolumn {i}"] for i in range(1, 9) if pd.notna(row[f"Kolumn {i}"])]
            ties = parse_ties(row["Ties"])
            
            if row["Speltyp"] == "En vinnare":
                ties[2] = ranking[1:]  # everyone except the winner tied for 2nd
            
            luck_modifier = LUCK.get(row["Spel"], 1.0) if use_luck else 1.0
            ratings = process_game(ratings, ranking, k * luck_modifier, ties)
    return pd.DataFrame(ratings.items(), columns=["Player", "Elo"]).set_index("Player").round(1)

def calculate_elo_over_time(groups, k=20, use_luck = True):
    ratings = {player: 1000 for player in PLAYERS}
    history = {player: [] for player in PLAYERS}
    dots = {player: [] for player in PLAYERS}
    dates = []
    all_games = pd.concat(groups.values()).sort_values("Datum")

    for index, row in all_games.iterrows():
        if row["Speltyp"] in ["Rankning", "En vinnare"]:
            ranking = [row[f"Kolumn {i}"] for i in range(1, 9) if pd.notna(row[f"Kolumn {i}"])]
            ties = parse_ties(row["Ties"])
            
            if row["Speltyp"] == "En vinnare":
                ties[2] = ranking[1:]  # everyone except the winner tied for 2nd
            
            luck_modifier = LUCK.get(row["Spel"], 1.0) if use_luck else 1.0
            ratings = process_game(ratings, ranking, k * luck_modifier, ties)
            dates.append(row["Datum"])
            for player in PLAYERS:
                history[player].append(ratings[player])  # always record for the line
                dots[player].append(ratings[player] if player in ranking else np.nan)  # only when playing

    dots_df = pd.DataFrame(dots, index=dates)
    history_df = pd.DataFrame(history, index=dates)
    fig, ax = plt.subplots(figsize=(14, 7))
    lines = {}
    for player in PLAYERS:
        line, = ax.plot(history_df.index, history_df[player], label=player)  # continuous line
        lines[player] = line.get_color()  # grab the auto-assigned color

    for player in PLAYERS:
        ax.plot(dots_df.index, dots_df[player], marker="o", markersize=4, linestyle="none", color=lines[player])
    if use_luck:
        ax.set_title("Elo Ratings Over Time")
    else:
        ax.set_title("Elo Ratings Over Time, no luck-factor")

    ax.set_xlabel("Date")
    ax.set_ylabel("Elo Rating")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return history_df

def plotting(data):
    plot_df = data.map(lambda x: x[0] if isinstance(x, tuple) else x)
    count_df = data.map(lambda x: x[1] if isinstance(x, tuple) else None)
    ax = plot_df.plot(kind="bar", figsize=(12, 6))
    plt.ylabel("Score")
    plt.xlabel("Player")
    plt.title("Results by Game Category")
    plt.xticks(rotation=45)
    max_per_category = plot_df.idxmax()
    for i, container in enumerate(ax.containers):
        category = plot_df.columns[i]
        max_player = max_per_category[category]
        for j, bar in enumerate(container):
            player = plot_df.index[j]
            if player == max_player:
                bar.set_edgecolor("gold")
                bar.set_linewidth(2.5)
            count = count_df.iloc[j, i]
            if pd.notna(count):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"n={int(count)}", ha="center", va="bottom", fontsize=7)
    plt.tight_layout()
    plt.show()

def main():
    df = read()
    groups = partition(df)
    #big = analyze(groups)
    #elo = calculate_elo(groups)
    #plotting(big)
    calculate_elo_over_time(groups, use_luck=False)

main()