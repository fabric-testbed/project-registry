#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)

# start local database
./run-local-database.sh

# launch the server
cd ../server

# variables
VENV_DIR=venv
PYTHON3_PATH=/usr/local/bin/python3

# check for virtualenv directory
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Unable to find virtualenv directory: ${VENV_DIR}, creating now"
  virtualenv -p $PYTHON3_PATH venv
fi

# install packages from requirements file
source venv/bin/activate
echo "[INFO] install requirements.txt"
pip install -r requirements.txt

# run development server
FLASK_ENV=development python -m swagger_server

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
