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

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def _get_init_player_data():
    try:
        response = requests.get(INIT_PLAYERS_URL)
        response.raise_for_status()
        data = response.json()
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

        # TODOROSS
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
    if request.is_json:
        player = request.get_json()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # TODOROSS
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

@app.route("/players", methods=["PUT"])
def update_player():
    if request.is_json:
        player = request.get_json()
        # TODOROSS
        a_id = player.get('id')
        a_name = player.get('name')
        a_type = player.get('type')

        if not a_id or not a_name or not a_type:
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"UPDATE {table_players} SET name = %s, type = %s WHERE id = %s"
            player_data = (a_name, a_type, a_id)
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
