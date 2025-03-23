"""
Run the API to manage data CRUD requests

Use via `python3 app.py` or `flask run`
"""

import os
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

SUPPLY_INIT_DATA=True

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# TODOROSS
init_players = [
    {"name": "Lexi", "type": "hamster"},
    {"name": "Lorelei", "type": "hamster"},
]

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
            name VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL
        )"""
        cursor.execute(query_players)

        if supply_init_data:
            query_check_empty = f"SELECT COUNT(*) FROM {table_players}"
            cursor.execute(query_check_empty)
            result = cursor.fetchone()

            # Only insert data during init if no data present
            if result[0] == 0:
                query_add_players = f"INSERT INTO {table_players} (name, type) VALUES (%s, %s)"
                players_data = [(player['name'], player['type']) for player in init_players]
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
