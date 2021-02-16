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
pip install -U pip
echo "[INFO] install requirements.txt"
pip install -r requirements.txt

# create database tables and load
cd ../dbmgmt
# drop and create all database tables
python drop_create_tables.py
# now run as a separate script after the project-registry is running since in needs to hit the /people endpoint
#python update_tables.py

# run production server using uwsgi
cd ../server
uwsgi --virtualenv ./venv --ini swagger_server/config/config.ini

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
