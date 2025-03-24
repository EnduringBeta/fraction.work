"""
Run the API to manage data CRUD requests

Use via `python3 app.py` or `flask run`
"""

import os
import requests
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

MYSQL_DATABASE=os.environ.get('MYSQL_DATABASE', 'mydatabase')
MYSQL_USER=os.environ.get('MYSQL_USER', 'myuser')
MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD', 'insecure')

table_players='players'

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE
}

INIT_PLAYERS_URL="https://api.hirefraction.com/api/test/baseball"

SUPPLY_INIT_DATA=True

class CleaningCounter:
    def __init__(self):
        self.caught_stealing_cleanings = 0
        self.avg_cleanings = 0
        self.on_base_cleanings = 0
        self.slugging_cleanings = 0
        self.combo_cleanings = 0

    def increment_caught_stealing(self):
        self.caught_stealing_cleanings += 1

    def increment_avg(self):
        self.avg_cleanings += 1

    def increment_on_base(self):
        self.on_base_cleanings += 1

    def increment_slugging(self):
        self.slugging_cleanings += 1

    def increment_combo(self):
        self.combo_cleanings += 1

    def print_cleaning_report(self):
        print(f"Cleaning report:")
        print(f"Caught stealing cleanings: {self.caught_stealing_cleanings}")
        print(f"Batting average % cleanings: {self.avg_cleanings}")
        print(f"On-base % cleanings: {self.on_base_cleanings}")
        print(f"Slugging % cleanings: {self.slugging_cleanings}")
        print(f"On-base & slugging combo cleanings: {self.combo_cleanings}")


def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def _clean_init_player(player, cleaning_counter):
    if isinstance(player["Caught stealing"], str):
        player["Caught stealing"] = 0
        cleaning_counter.increment_caught_stealing()

    player_hits = player["Hits"]
    player_doubles = player["Double (2B)"]
    player_triples = player["third baseman"]
    player_home_runs = player["home run"]
    player_at_bat = player["At-bat"]

    player_calc_avg = player_hits / player_at_bat

    # https://en.wikipedia.org/wiki/List_of_Major_League_Baseball_career_on-base_percentage_leaders
    player_calc_on_base = (player_hits + player["a walk"]) / (player_at_bat + player["a walk"])

    # https://en.wikipedia.org/wiki/Slugging_percentage
    player_calc_singles = player_hits - player_doubles - player_triples - player_home_runs
    player_calc_slugging = (player_calc_singles + 2*player_doubles
        + 3*player_triples + 4*player_home_runs) / player_at_bat

    player_calc_on_base_plus_slugging = player_calc_on_base + player_calc_slugging

    if player["AVG"] != player_calc_avg:
        player["AVG"] = player_calc_avg
        cleaning_counter.increment_avg()

    if player["On-base Percentage"] != player_calc_on_base:
        player["On-base Percentage"] = player_calc_on_base
        cleaning_counter.increment_on_base()

    if player["Slugging Percentage"] != player_calc_slugging:
        player["Slugging Percentage"] = player_calc_slugging
        cleaning_counter.increment_slugging()

    if player["On-base Plus Slugging"] != player_calc_on_base_plus_slugging:
        player["On-base Plus Slugging"] = player_calc_on_base_plus_slugging
        cleaning_counter.increment_combo()

    return player

def _get_init_player_data():
    try:
        response = requests.get(INIT_PLAYERS_URL)
        response.raise_for_status()
        data = response.json()

        cleaning_counter = CleaningCounter()

        # Clean data
        for player in data:
            _clean_init_player(player, cleaning_counter)

        cleaning_counter.print_cleaning_report()

        return data
    except Exception as e:
        print(f"Error getting initial player data: {e}")
        raise e

def _initialize_db(supply_init_data = False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create database if it doesn't exist
        query_database = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"
        cursor.execute(query_database)
        conn.commit()

        # Create players table if it doesn't exist
        query_players = f"""CREATE TABLE IF NOT EXISTS {table_players} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_name VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            games INT NOT NULL,
            at_bat INT NOT NULL,
            runs INT NOT NULL,
            hits INT NOT NULL,
            doubles INT NOT NULL,
            triples INT NOT NULL,
            home_runs INT NOT NULL,
            rbi INT NOT NULL,
            walks INT NOT NULL,
            strikeouts INT NOT NULL,
            stolen_bases INT NOT NULL,
            caught_stealing INT NOT NULL,
            batting_average FLOAT NOT NULL,
            on_base_percent FLOAT NOT NULL,
            slugging_percent FLOAT NOT NULL,
            on_base_plus_slugging FLOAT NOT NULL
        )"""
        cursor.execute(query_players)

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_players}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                # Get players data
                players = _get_init_player_data()

                if not players:
                    print(f"Error getting initial player data!")
                    conn.commit()
                    conn.close()
                    return

                query_add_players = f"INSERT INTO {table_players} \
                (player_name, position, games, at_bat, runs, hits, \
                doubles, triples, home_runs, rbi, walks, strikeouts, \
                stolen_bases, caught_stealing, batting_average, \
                on_base_percent, slugging_percent, on_base_plus_slugging) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                players_data = [(
                    player['Player name'],
                    player['position'],
                    player['Games'],
                    player['At-bat'],
                    player['Runs'],
                    player['Hits'],
                    player['Double (2B)'],
                    player['third baseman'],
                    player['home run'],
                    player['run batted in'],
                    player['a walk'],
                    player['Strikeouts'],
                    player['stolen base'],
                    player['Caught stealing'],
                    player['AVG'],
                    player['On-base Percentage'],
                    player['Slugging Percentage'],
                    player['On-base Plus Slugging'],
                ) for player in players]
                cursor.executemany(query_add_players, players_data)
                print('Added initial players!')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

# Ensure database is initialized
with app.app_context():
    _initialize_db(SUPPLY_INIT_DATA)

@app.route('/')
def index():
    return 'No players here... Try "/players" or port 3000!'

@app.get("/players")
def get_players():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_players}"
        cursor.execute(query)
        players = cursor.fetchall()
        conn.close()

        # Return players
        # Flask doesn’t automatically convert lists to JSON
        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_players} WHERE id = %s"
        cursor.execute(query, (player_id,))
        player = cursor.fetchone()
        conn.close()

        if not player:
            return jsonify({"error": "Player not found"}), 404

        # Return player
        return jsonify(player), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/players")
def add_player():
    return jsonify({"error": "Adding players is not implemented"}), 500
    if request.is_json:
        player = request.get_json()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # TODO
            query = f"INSERT INTO {table_players} (name, type) VALUES (%s, %s)"
            player_data = (player['name'], player['type'])
            cursor.execute(query, player_data)
            conn.commit()
            conn.close()

            # Player added
            return jsonify({'message': 'Player added successfully!'}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

# TODOROSS - test
@app.route("/players", methods=["PUT"])
def update_player():
    if request.is_json:
        player = request.get_json()

        p_id = player.get('id')
        p_player_name = player.get('player_name')
        p_position = player.get('position')
        p_games = player.get('games')
        p_at_bat = player.get('at_bat')
        p_runs = player.get('runs')
        p_hits = player.get('hits')
        p_doubles = player.get('doubles')
        p_triples = player.get('triples')
        p_home_runs = player.get('home_runs')
        p_rbi = player.get('rbi')
        p_walks = player.get('walks')
        p_strikeouts = player.get('strikeouts')
        p_stolen_bases = player.get('stolen_bases')
        p_caught_stealing = player.get('caught_stealing')
        p_batting_average = player.get('batting_average')
        p_on_base_percent = player.get('on_base_percent')
        p_slugging_percent = player.get('slugging_percent')
        p_on_base_plus_slugging = player.get('on_base_plus_slugging')
        print(p_id)
        print(p_player_name)
        print(p_position)
        print(p_games)
        print(p_at_bat)
        print(p_runs)
        print(p_hits)
        print(p_doubles)
        print(p_triples)
        print(p_home_runs)
        print(p_rbi)
        print(p_walks)
        print(p_strikeouts)
        print(p_stolen_bases)
        print(p_caught_stealing)
        print(p_batting_average)
        print(p_on_base_percent)
        print(p_slugging_percent)
        print(p_on_base_plus_slugging)

        if (not p_id or not p_player_name or not p_position or not p_games or not p_at_bat
            or not p_runs or not p_hits or not p_doubles or not p_triples or not p_home_runs
            or not p_rbi or not p_walks or not p_strikeouts or not p_stolen_bases
            or not p_caught_stealing or not p_batting_average or not p_on_base_percent
            or not p_slugging_percent or not p_on_base_plus_slugging):
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"UPDATE {table_players} SET player_name = %s, position = %s, games = %s, \
                at_bat = %s, runs = %s, hits = %s, doubles = %s, triples = %s, home_runs = %s, \
                rbi = %s, walks = %s, strikeouts = %s, stolen_bases = %s, caught_stealing = %s, \
                batting_average = %s, on_base_percent = %s, slugging_percent = %s, \
                on_base_plus_slugging = %s, WHERE id = %s"
            # No ID
            player_data = (
                p_player_name,
                p_position,
                p_games,
                p_at_bat,
                p_runs,
                p_hits,
                p_doubles,
                p_triples,
                p_home_runs,
                p_rbi,
                p_walks,
                p_strikeouts,
                p_stolen_bases,
                p_caught_stealing,
                p_batting_average,
                p_on_base_percent,
                p_slugging_percent,
                p_on_base_plus_slugging,
            )
            cursor.execute(query, player_data)
            conn.commit()
            conn.close()

            # No data found/changed
            if cursor.rowcount == 0:
                return jsonify({"error": "Player not found"}), 404

            # Player updated
            return jsonify({"message": "Player updated successfully!"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 415

@app.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM {table_players} WHERE id = %s"
        cursor.execute(query, (player_id,))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Player not found"}), 404

        # Player removed
        return jsonify({"message": "Player deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
