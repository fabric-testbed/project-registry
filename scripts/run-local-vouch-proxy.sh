#!/usr/bin/env bash

# run this script from the scripts directory
VOUCH_PROXY_CONTAINER=pr-vouch-proxy
NGINX_CONTAINER=pr-nginx
SCRIPTS_DIR=$(pwd)
cd ../

# check for previously running vouch-proxy container
PREV_VOUCH_PROXY=$(docker ps -a | grep ${VOUCH_PROXY_CONTAINER})
if [ -n "${PREV_VOUCH_PROXY}" ]; then
  VOUCH_PROXY_ID=$(echo $PREV_VOUCH_PROXY | cut -d ' ' -f 1)
  echo "[INFO] Found previously running vouch-proxy: ${VOUCH_PROXY_ID}, stopping/removing now"
  docker stop ${VOUCH_PROXY_ID}
  docker rm -fv ${VOUCH_PROXY_ID}
fi

# check for previously running nginx container
PREV_NGINX=$(docker ps -a | grep ${NGINX_CONTAINER})
if [ -n "${PREV_NGINX}" ]; then
  NGINX_ID=$(echo $PREV_NGINX | cut -d ' ' -f 1)
  echo "[INFO] Found previously running nginx: ${NGINX_ID}, stopping/removing now"
  docker stop ${NGINX_ID}
  docker rm -fv ${NGINX_ID}
fi

# start nginx and vouch-proxy containers
docker-compose up -d nginx vouch-proxy

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
