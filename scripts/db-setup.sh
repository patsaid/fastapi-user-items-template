#!/bin/sh

export PGUSER="postgres"
psql -c "CREATE DATABASE db;"

psql db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"