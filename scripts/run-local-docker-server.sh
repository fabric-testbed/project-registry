#!/usr/bin/env bash

# run this script from the scripts directory
API_SERVER_CONTAINER=pr-api-server
SERVER_BUILD_WAIT_TIME=45
SCRIPTS_DIR=$(pwd)

# start local database
./run-local-database.sh

# start local vouch-proxy
./run-local-vouch-proxy.sh

# launch the server
cd ../

# check for previously running database container
PREV_API_SERVER=$(docker ps -a | grep ${API_SERVER_CONTAINER})
if [ -n "${PREV_DB}" ]; then
  API_SERVER_ID=$(echo $PREV_API_SERVER | cut -d ' ' -f 1)
  echo "[INFO] Found previously running database: ${API_SERVER_ID}, stopping/removing now"
  docker stop ${API_SERVER_ID}
  docker rm -fv ${API_SERVER_ID}
fi

# run development server in
echo "[INFO] run development server in docker"
docker-compose pull
docker-compose build
docker-compose up -d api-server

# wait for server to start up
echo "[INFO] waiting for server to start up"
for pc in $(seq ${SERVER_BUILD_WAIT_TIME} -1 1); do
  echo -ne "$pc ...\033[0K\r" && sleep 1
done
echo ""

# create the database tables and load initial data
# drop and create all database tables
drop_create_tables='source ./.venv/bin/activate && cd /dbmgmt/ && python drop_create_tables.py'
docker exec pr-api-server /bin/bash -c "${drop_create_tables}"
# now run as a separate script after the project-registry is running since in needs to hit the /people endpoint
#update_tables='source ./.venv/bin/activate && cd /dbmgmt/ && python update_tables.py'
#docker exec pr-api-server /bin/bash -c "${update_tables}"

# provide user with deployment information
echo ""
echo "[INFO] server running at: http://127.0.0.1:8080/ui/#/"
echo "[INFO] when finished terminate using command:"
echo "       ctrl-c               # to detach from container shell"
echo "       docker-compose stop  # to stop the running containers"
echo ""
sleep 1

# show api-server STDOUT to user
docker attach --sig-proxy=false pr-api-server

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0
