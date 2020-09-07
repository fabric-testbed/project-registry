#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)
cd ../

# variables
STUB_DIR=server-stub
FILES_TO_COPY=(
  requirements.txt
  swagger_server/__main__.py
  swagger_server/__init__.py
  swagger_server/config.py
  wsgi.py
)

DIRS_TO_COPY=(
  swagger_server/auth
  swagger_server/database
  swagger_server/ini
  swagger_server/response_code
  ini
)

# check for new server-stub directory
if [ ! -d "$STUB_DIR" ]; then
  echo "[ERROR] Unable to find ${STUB_DIR}"
fi

# copy directories from server to new server-stub
for f in "${DIRS_TO_COPY[@]}"; do
  echo "[INFO] copy directory: ${f} to new server-stub"
  cp -r server/${f} $STUB_DIR/${f}
done

# copy files from server to new server-stub
for f in "${FILES_TO_COPY[@]}"; do
  echo "[INFO] copy file: ${f} to new server-stub"
  cp server/${f} $STUB_DIR/${f}
done

# update controllers
echo "[INFO] update controllers to include response_code import"
while read f; do
  echo "---------------------------------------------------"
  echo "[INFO] updating file: ${f}"
  sed -i "/from swagger_server import util/a from swagger_server.response_code import ${f%???} as rc" \
    $STUB_DIR/swagger_server/controllers/${f}
  while read line; do
    if [[ $line == def* ]]; then
      echo "  - ${line}"
      func_name=$(echo $line | cut -d ':' -f 1 | cut -d ' ' -f 2-)
      echo "    ${func_name//=None/}"
      sed -i "0,/'do some magic!'/s//rc.${func_name//=None/}/" $STUB_DIR/swagger_server/controllers/${f}
    fi
  done < <(cat $STUB_DIR/swagger_server/controllers/${f})
done < <(ls -1 $STUB_DIR/swagger_server/controllers | grep -v '^__*')

# replace server with new server-stub
echo "[TODO] remove existing server directory and rename server-stub to server"

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0;
