#!/usr/bin/env bash

_set_docker_uwsgi_ini() {
    > docker_uwsgi.ini
    echo "[uwsgi]" >> docker_uwsgi.ini
    echo "; ### DOCKER USE ONLY ###" >> docker_uwsgi.ini
    echo ";     documentation: http://uwsgi-docs.readthedocs.io/en/latest/Options.html" >> docker_uwsgi.ini
    echo ";     do not check this file into the repository" >> docker_uwsgi.ini
    echo ";" >> docker_uwsgi.ini
    echo "buffer-size = 32768" >> docker_uwsgi.ini
    echo "enable-threads = true" >> docker_uwsgi.ini
    echo "protocol = http" >> docker_uwsgi.ini
    echo "processes = 8" >> docker_uwsgi.ini
    echo "threads = 8" >> docker_uwsgi.ini
    echo "chdir = ./" >> docker_uwsgi.ini
    echo "module = wsgi:app" >> docker_uwsgi.ini
    echo "master = true" >> docker_uwsgi.ini
    echo "socket = :5000" >> docker_uwsgi.ini
    echo "vacuum = true" >> docker_uwsgi.ini
    echo "max-requests = 5000" >> docker_uwsgi.ini
    echo "die-on-term = true" >> docker_uwsgi.ini
}

if [[ "$1" = 'run_server' ]]; then
    # set connexion.ini file
    _set_docker_uwsgi_ini

    # setup virtual environment
    export PYTHONPATH=$(pwd)
    pip install virtualenv
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    # update swagger.yaml file
    if [[ ! -z ${SWAGGER_HOST} ]]; then
        sed -i '/servers:/!b;n;c- url: http://'${SWAGGER_HOST}'/' /server/swagger_server/swagger/swagger.yaml
    fi

    # run the server
    uwsgi --virtualenv ./.venv --ini docker_uwsgi.ini
else
    exec "$@"
fi
