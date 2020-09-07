#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)
cd ../

# check for previously running database container
PREV_DB=$(docker ps | grep api-db)
if [ -n "${PREV_DB}" ]; then
  DB_ID=$(echo $PREV_DB | cut -d ' ' -f 1)
  echo "[INFO] Found previously running DB: ${DB_ID}, stopping/removing now"
  docker stop ${DB_ID}
  docker rm ${DB_ID}
fi

docker-compose up -d database

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
