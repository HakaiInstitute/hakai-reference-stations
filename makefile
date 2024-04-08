# Makefile

# 'make lint' will run the linting commands
lint:
	ruff check . --select I --fix && ruff format .

get-db-stations:
	poetry run python hakai_reference_stations/load_from_database.py

build:
	poetry run python hakai_reference_stations/map.py
	