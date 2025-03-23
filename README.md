# fraction.work web app

Example building container with database, data retrieved by API, and UI to view

This uses Docker with Linux, MySQL, Python, and React with JS

## Containerized Setup

0. Clone this repository first: `git clone git@github.com:EnduringBeta/fraction.work.git`

### Run Docker container

1. Download [Docker Desktop](https://www.docker.com/) and install. Probably sign in. (This program is useful, but following steps will only use the command line functionality.)
2. Inside the repo directory from step 0, run `docker build -t fraction.work .` to build the Docker image
3. Run `docker run -d -p 3306:3306 -p 5000:5000 -p 3000:3000 fraction.work` to start the MySQL and Flask server

These can also be run together via `redocker.sh`

### Test server

# TODOROSS

4. Go to http://localhost:5000/animals
5. Add an animal via: `curl -i http://127.0.0.1:5000/animals -X POST -H 'Content-Type: application/json' -d '{"name":"Wren", "type": "cat"}'`
6. Update an animal via: `curl -i http://127.0.0.1:5000/animals -X PUT -H 'Content-Type: application/json' -d '{"id": 5, "name":"Sparrow", "type": "cat"}'`
7. Get a single animal via: http://127.0.0.1:5000/animals/2
8. Remove an animal via: `curl -i http://127.0.0.1:5000/animals/4 -X DELETE -H 'Content-Type: application/json'`
9. Go to http://localhost:3000

## Local Setup

Clone the repo, create Python virtual environment, install Python requirements, install MySQL, and run `./run-app.sh`, which starts the server API (`python3 app.py` and `flask run` also work).

Environment variables may break things; running locally is untested.

## Troubleshooting

* On Docker run, "Bind for 0.0.0.0:3306 failed: port is already allocated" - stop existing Docker container

## Tips

* `SELECT user FROM mysql.user;`
* `SHOW DATABASES;`

## TODO

* Ideally MySQL, Flask, and React are in separate containers
* Enable running locally more easily
