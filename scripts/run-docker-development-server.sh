#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)
cd ../

# variables
VENV_DIR=venv
PYTHON3_PATH=/usr/local/bin/python3

# run development server in
echo "[INFO] run development server in docker"
docker-compose pull
docker-compose build
docker-compose up server nginx

# provide user with deployment information
echo "[INFO] server running at: http://127.0.0.1:5000/ui/#/"
echo "[INFO] when finished terminate using command:"
echo "       docker-compose stop"

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
