#!/bin/bash

echo "Starting fraction.work web app..."

# Assuming in proper working directory

# Start MySQL in background and run initial SQL script to create database and user
service mysql start && mysql -u root -p$MYSQL_PASSWORD < $REPO_DIR/init.sql

# Activate Python virtual environment, which is assumed to have been set up parallel to repo
. venv/bin/activate

# TODOROSS: pass environment var for OpenAI

# Run the API (in background with "&")!
# Use host arg for all addresses
flask run --host=0.0.0.0 --port=5000 &
#python3 app.py

# Run the UI!
cd $REPO_DIR/ui/ && npm start

echo "Ending fraction.work web app..."
