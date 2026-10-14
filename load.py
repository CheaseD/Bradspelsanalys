import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read():
    # Read file
    df = pd.read_csv("KTK Board Games - Speldata.csv")
    return df

def partition(df):
    # Define partitions/groups
    groups_map = {
        "Stora spel": ["Terraforming Mars", "Great Western Trail", "Wingspan", "Root", "Shogun"], #90min+
        "Medel spel": ["Parks", "Terraforming Mars: The Dice Game", "Flamme Rouge", #30-90min
                    "Quacks of Quedlingburg", "Treasure Island", "Bohnanza",
                    "6 Nimmt", "Dominion", "7 Wonders", "Galaxy Trucker"],
        "Små spel": ["Durak", "For Sale", "Wizard", "Scout", "Coup", "Ya Blew It", # <30min
                    "Railroad Ink"], 
    } #Not included: Hanabi (1), The Crew (2), Magic Maze (2), Secret Hitler (1)


    groups = {
        name: df[df["Spel"].isin(keywords)]
        for name, keywords in groups_map.items()
    }

    return groups

def analyze(groups):
    mega_results = {}
    total_points = {}
    players = ["Silas", "Lage", "Zeno", "Josie", "Miriam", "Felipe", "John", "Vilmos", "William", "Lilly", "Elsa", "Lukas"]
    for player in players:
        total_points[player] = np.array([0.0, 0.0])

    for name, group in groups.items():
        results = {}
        points = {}
        players = ["Silas", "Lage", "Zeno", "Josie", "Miriam", "Felipe", "John", "Vilmos", "William", "Lilly", "Elsa", "Lukas"]
        for player in players:
            points[player] = np.array([0.0, 0.0])
        for index, row in group.iterrows(): #TODO: Lägg till när man delar på en plats
            if row["Speltyp"] == "Rankning":
                num_p = float(row["Antal Spelare"])
                points[row["Kolumn 1"]] += np.array([1.0, 1.0])
                points[row["Kolumn 2"]] += np.array([1 - 1/(num_p - 1), 1])
                if pd.notna(row["Kolumn 3"]):
                    points[row["Kolumn 3"]] += np.array([1 - 2/(num_p - 1), 1])
                if pd.notna(row["Kolumn 4"]):
                    points[row["Kolumn 4"]] += np.array([1 - 3/(num_p - 1), 1]) 
                if pd.notna(row["Kolumn 5"]):
                    points[row["Kolumn 5"]] += np.array([1 - 4/(num_p - 1), 1]) 
                if pd.notna(row["Kolumn 6"]):
                    points[row["Kolumn 6"]] += np.array([1 - 5/(num_p - 1), 1]) 
                if pd.notna(row["Kolumn 7"]):
                    points[row["Kolumn 7"]] += np.array([1 - 6/(num_p - 1), 1]) 
                if pd.notna(row["Kolumn 8"]):
                    points[row["Kolumn 8"]] += np.array([1 - 7/(num_p - 1), 1]) 

            elif row["Speltyp"] == "En vinnare":
                num_p = float(row["Antal Spelare"]) #(playerAmount*playerAmount-3*playerAmount+2)/(2*(playerAmount-1)*(playerAmount-1)
                points[row["Kolumn 1"]] += np.array([1, 1])
                points[row["Kolumn 2"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1])
                if pd.notna(row["Kolumn 3"]):
                    points[row["Kolumn 3"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1])
                if pd.notna(row["Kolumn 4"]):
                    points[row["Kolumn 4"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1]) 
                if pd.notna(row["Kolumn 5"]):
                    points[row["Kolumn 5"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1])
                if pd.notna(row["Kolumn 6"]):
                    points[row["Kolumn 6"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1]) 
                if pd.notna(row["Kolumn 7"]):
                    points[row["Kolumn 7"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1]) 
                if pd.notna(row["Kolumn 8"]):
                    points[row["Kolumn 8"]] += np.array([(num_p**2 - 3 * num_p + 2)/(2 * (num_p - 1)**2), 1]) 
        
        for key, value in points.items():
            results[key] = (round(value[0]/value[1], 2), int(value[1]))
            total_points[key] += value

        mega_results[name] = results
    
    mega_results["Totalt"] = {}
    for key, value in total_points.items():
        mega_results["Totalt"][key] = (round(value[0]/value[1], 2), int(value[1]))
    mega_df = pd.DataFrame(mega_results)
    return mega_df

def calculate_elo(groups, k=64):
    players = ["Silas", "Lage", "Zeno", "Josie", "Miriam", "Felipe", "John", "Vilmos", "William", "Lilly", "Elsa", "Lukas"]
    ratings = {player: 1000 for player in players} #Start ELO

    luck = {
    "Terraforming Mars": 0.85,
    "Great Western Trail": 0.9,
    "Wingspan": 0.75,
    "Root": 0.8,
    "Shogun": 0.7,
    "Parks": 0.7,
    "Terraforming Mars: The Dice Game": 0.55,
    "Flamme Rouge": 0.75,
    "Quacks of Quedlingburg": 0.4,  # very luck dependent
    "Treasure Island": 0.65, #Not in use because not of speltyp "Rankning"
    "Bohnanza": 0.6,
    "6 Nimmt": 0.55,
    "Dominion": 0.7,
    "7 Wonders": 0.7, #INGEN ANING, ALDRIG SPELAT
    "Galaxy Trucker": 0.6, #ALDRIG SPELAT
    "Durak": 0.65,
    "For Sale": 0.6,
    "Wizard": 0.65,
    "Scout": 0.6,
    "Coup": 0.65,
    "Ya Blew It": 0.45,
    "Railroad Ink": 0.55
}

    def expected_score(rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def process_game(ratings, ranking, k_adjusted):
        new_ratings = ratings.copy()
        for i in range(len(ranking)):
            for j in range(i + 1, len(ranking)):
                winner = ranking[i]
                loser = ranking[j]
                new_ratings[winner] = update_elo(ratings[winner], ratings[loser], 1, k_adjusted)
                new_ratings[loser] = update_elo(ratings[loser], ratings[winner], 0, k_adjusted)
        return new_ratings

    def update_elo(rating_a, rating_b, score_a, k_adjusted):
        expected = expected_score(rating_a, rating_b)
        return rating_a + k_adjusted * (score_a - expected)

    for name, group in groups.items():
        for index, row in group.iterrows():
            if row["Speltyp"] == "Rankning":
                game_luck = luck.get(row["Spel"], 1.0)  # default to 1.0 if not found
                ranking = [row[f"Kolumn {i}"] for i in range(1, 9) if pd.notna(row[f"Kolumn {i}"])]
                ratings = process_game(ratings, ranking, k * game_luck)

    elo_df = pd.DataFrame(ratings.items(), columns=["Player", "Elo"]).set_index("Player").round(1)
    return elo_df

def plotting(data: dict): #egentligen är data en dataframe(tror jag)
    plot_df = data.map(lambda x: x[0] if isinstance(x, tuple) else x)
    count_df = data.map(lambda x: x[1] if isinstance(x, tuple) else None)

    ax = plot_df.plot(kind="bar", figsize=(12, 6))
    plt.ylabel("Score")
    plt.xlabel("Player")
    plt.title("Results by Game Category")
    plt.xticks(rotation=45)

    max_per_category = plot_df.idxmax()

    # Annotate each bar with the count
    for i, container in enumerate(ax.containers):
        category = plot_df.columns[i]
        max_player = max_per_category[category]
        for j, bar in enumerate(container):
            player = plot_df.index[j]
            # Highlight the max bar
            if player == max_player:
                bar.set_edgecolor("gold")
                bar.set_linewidth(2.5)
            count = count_df.iloc[j, i]
            if pd.notna(count):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"n={int(count)}",
                    ha="center", va="bottom", fontsize=7
                )

    plt.tight_layout()
    plt.show()

def calculate_elo_over_time(groups, k=32):
    players = ["Silas", "Lage", "Zeno", "Josie", "Miriam", "Felipe", "John", "Vilmos", "William", "Lilly", "Elsa", "Lukas"]
    ratings = {player: 1000 for player in players}
    history = {player: [] for player in players}
    dates = []

    def expected_score(rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_elo(rating_a, rating_b, score_a, k_adjusted):
        expected = expected_score(rating_a, rating_b)
        return rating_a + k_adjusted * (score_a - expected)

    def process_game(ratings, ranking, k_adjusted, ties={}):
        new_ratings = ratings.copy()
        place_of = {}
        for i, player in enumerate(ranking):
            place_of[player] = i + 1
        for place, tied_players in ties.items():
            for player in tied_players:
                place_of[player] = place
        for i in range(len(ranking)):
            for j in range(i + 1, len(ranking)):
                winner = ranking[i]
                loser = ranking[j]
                if place_of[winner] == place_of[loser]:
                    score = 0.5
                else:
                    score = 1.0
                new_ratings[winner] = update_elo(ratings[winner], ratings[loser], score, k_adjusted)
                new_ratings[loser] = update_elo(ratings[loser], ratings[winner], 1 - score, k_adjusted)
        return new_ratings

    # Combine and sort all games by date
    all_games = pd.concat(groups.values()).sort_values("Datum")

    for index, row in all_games.iterrows():
        if row["Speltyp"] in ["Rankning", "En vinnare"]:
            ranking = [row[f"Kolumn {i}"] for i in range(1, 9) if pd.notna(row[f"Kolumn {i}"])]
            ties = parse_ties(row["Annotations"])
            game_luck = luck.get(row["Spel"], 1.0)
            ratings = process_game(ratings, ranking, k * game_luck, ties)

            # Record ratings after this game
            dates.append(row["Datum"])
            for player in players:
                history[player].append(ratings[player])

    # Plot
    history_df = pd.DataFrame(history, index=dates)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    for player in players:
        ax.plot(history_df.index, history_df[player], label=player, marker="o", markersize=3)

    ax.set_title("Elo Ratings Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Elo Rating")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return history_df

def main():
    df = read()
    groups = partition(df)
    big = analyze(groups)
    calculate_elo_over_time(groups)
    

main()