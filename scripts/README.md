# Scripts

The scripts in this directory are used to deploy, update, or otherwise run code on various systems

```console
$ tree -L 1 scripts
scripts
├── README.md                     # Description of each script
├── run-local-database.sh         # Helper script to launch database
├── run-local-docker-server.sh    # Run using docker for all components
├── run-local-flask-server.sh     # Run using Flask development server
├── run-local-uwsgi-server.sh     # Run using uWSGI server
├── run-local-vouch-proxy.sh      # Helper script to launch Vouch-Proxy and Nginx
└── update-swagger-stub.sh        # Format new python-flask export from swagger
```

## script: `run-local-database.sh`

Helper script used to launch the database from other scripts (not used directly)

## script: `run-local-docker-server.sh`

### Usage

Run using docker for all components

```console
./run-local-docker-server.sh
```

Example provide on main README of repository

## script: `run-local-flask-server.sh`

Run using Flask development server. Good for interactive development as the development server will automatically attempt to restart on code changes (server will abort on error).

### Usage

```console
run-local-flask-server.sh
```

## script: `run-local-uwsgi-server.sh`

Run using uWSGI server. Good for final testing prior to full docker deployment since this is the code that docker will run.

### Usage

```console
./run-local-uwsgi-server.sh
```

## script: `run-local-vouch-proxy.sh`

Helper script used to launch vouch-proxy and nginx from other scripts (not used directly)


## script: `update-swagger-stub.sh`

Whenever a modification is made to the Swagger specification file a new python-flask server stub is made to reflect the changes. The new stub code is insufficient to run the production server as it is, and must have some modifications made to it prior to being run. This script is used to update the newly generated stub files to match the server deployment patterns.

### Usage

Copy the directory created by a python-flask Server Stub export as `server-stub` at the same level as the `server` directory.

```console
./update-swagger-stub.sh
```

The newly generated files from Swagger are altered in place using `sed` to reference the code found in the `swagger_server/response_code` directory which is copied over from the prior deployment.

Upon completion rename the old and new server exports from swaggerhub

```console
mv server server-old
mv server-stub server
```

On occasion some manual tweaking is necessary in the updated `controllers` directory.
