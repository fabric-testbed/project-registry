#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)

# start local database
./run-local-database.sh

# start local vouch-proxy
./run-local-vouch-proxy.sh

# launch the server
cd ../server
export PYTHONPATH=$(pwd)

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

# create database tables and load
cd ../dbmgmt
python drop_create_tables.py
python load_initial_data.py

# run production server using uwsgi
cd ../server
uwsgi --virtualenv ./venv --ini swagger_server/config/config.ini

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
