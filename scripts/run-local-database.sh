#!/usr/bin/env bash

# run this script from the scripts directory
DB_CONTAINER=pr-database
SCRIPTS_DIR=$(pwd)
cd ../

# check for previously running database container
PREV_DB=$(docker ps -a | grep ${DB_CONTAINER})
if [ -n "${PREV_DB}" ]; then
  DB_ID=$(echo $PREV_DB | cut -d ' ' -f 1)
  echo "[INFO] Found previously running database: ${DB_ID}, stopping/removing now"
  docker stop ${DB_ID}
  docker rm -fv ${DB_ID}
fi

# start database container
docker-compose up -d database

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
