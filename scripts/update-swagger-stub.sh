#!/usr/bin/env bash

# run this script from the scripts directory
SCRIPTS_DIR=$(pwd)
cd ../

# variables
# variables
STUB_DIR=python-flask-server-generated
WORKING_DIR=server
ARCHIVE_DIR=server_archive
SCRIPTS_DIR=$(pwd)

FILES_TO_COPY=(
    project-registry.ini
    swagger_server/__main__.py
    swagger_server/__init__.py
    swagger_server/db.py
    swagger_server/db_models.py
    swagger_server/db_load.py
    swagger_server/db_verify.py
)

DIRS_TO_COPY=(
    swagger_server/response_code
)

# check for STUB_DIR directory
if [ ! -d "$STUB_DIR" ]; then
    echo "[ERROR] Unable to find ${STUB_DIR}"
    exit 1
fi

# remove ARCHIVE_DIR and create new ARCHIVE_DIR from current WORKING_DIR
if [ -d "$ARCHIVE_DIR" ]; then
    rm -rf $ARCHIVE_DIR
fi
echo "[INFO] full copy of '${WORKING_DIR}' archived as '${ARCHIVE_DIR}'"
cp -r $WORKING_DIR $ARCHIVE_DIR

# create new WORKING_DIR
if [ -d "$WORKING_DIR" ]; then
    rm -rf $WORKING_DIR
fi
echo "[INFO] create new '${WORKING_DIR}' from '${STUB_DIR}'"
cp -r $STUB_DIR $WORKING_DIR

# copy relevant directories from ARCHIVE_DIR to new WORKING_DIR
for f in "${DIRS_TO_COPY[@]}"; do
    echo "[INFO] copy directory: ${f} to new ${WORKING_DIR}"
    cp -r $ARCHIVE_DIR/${f} $WORKING_DIR/${f}
done

# copy relevant files from ARCHIVE_DIR to new WORKING_DIR
for f in "${FILES_TO_COPY[@]}"; do
    echo "[INFO] copy file: ${f} to new ${WORKING_DIR}"
    cp $ARCHIVE_DIR/${f} $WORKING_DIR/${f}
done

# update controllers
echo "[INFO] update controllers to include response_code import"
while read f; do
    echo "---------------------------------------------------"
    echo "[INFO] updating file: ${f}"
    sed -i "/from swagger_server import util/a from swagger_server.response_code import ${f%???} as rc" \
        $WORKING_DIR/swagger_server/controllers/${f}
    while read line; do
        if [[ $line == def* ]]; then
            echo "  - ${line}"
            func_name=$(echo $line | cut -d ':' -f 1 | cut -d ' ' -f 2-)
            echo "    ${func_name//=None/}"
            sed -i "0,/'do some magic!'/s//rc.${func_name//=None/}/" $WORKING_DIR/swagger_server/controllers/${f}
        fi
    done < <(cat $WORKING_DIR/swagger_server/controllers/${f})
done < <(ls -1 $WORKING_DIR/swagger_server/controllers | grep -v '^__*')

# completed
echo "[INFO] completed - check files prior to use"

# return to scripts directory and exit
cd $SCRIPTS_DIR || exit 0
