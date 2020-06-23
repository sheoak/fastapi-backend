#! /usr/bin/env bash

# Let the DB start
# Not useful without docker?
# python scripts/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python initial_data.py
