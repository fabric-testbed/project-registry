# Scripts

The scripts in this directory are used to deploy, update, or otherwise run code on various systems

## script: `update-swagger-stub.sh`

Whenever a modification is made to the Swagger specification file a new python-flask server stub is made to reflect the changes. The new stub code is insufficient to run the production server as it is, and must have some modifications made to it prior to being run. This script is used to update the newly generated stub files to match the server deployment patterns.

### Usage

Copy the directory created by a python-flask Server Stub export as `server-stub` at the same level as the `server` directory

```console
cd scripts
./update-swagger-stub.sh
```

Files effected:

```
FILES_TO_COPY=(
  requirements.txt              # copied from prior deployment
  swagger_server/__main__.py    # copied from prior deployment
  swagger_server/__init__.py    # copied from prior deployment
  swagger_server/config.py      # copied from prior deployment
  wsgi.py                       # copied from prior deployment
)

DIRS_TO_COPY=(
  swagger_server/auth           # copied from prior deployment
  swagger_server/database       # copied from prior deployment
  swagger_server/ini            # copied from prior deployment
  swagger_server/response_code  # copied from prior deployment
  ini
)

swagger_server/controllers/*    # files altered in place (sed)
```
The newly generated files from Swagger are altered in place using `sed` to reference the code found in the `swagger_server/response_code` directory which is copied over from the prior deployment.

## script: `run-local-database.sh`

This script is designed to run the local database as defined in the `docker-compose.yml` file using the configuration found in `ini/pr_database.ini`.

```console
./run-local-database.sh
```

## script: `run-local-flask-server.sh`

This script is designed to run the local development server on port 5000.

```console
./run-local-flask-server.sh
```

The Swagger UI will be found at [http://127.0.0.1:5000/ui/#/](http://127.0.0.1:5000/ui/#/)

## script: `run-local-uwsgi-server.sh`

This script is designed to run the local production server on port 5000.

```console
./run-local-uwsgi-server.sh
```

The Swagger UI will be found at [http://127.0.0.1:5000/ui/#/](http://127.0.0.1:5000/ui/#/)

## script: `run-docker-development-server.sh`

Run the docker development server on port 8080

```console
./run-docker-development-server.sh
```
