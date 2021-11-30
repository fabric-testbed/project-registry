#!/usr/bin/env python3

import os
from logging import Formatter
from logging.config import dictConfig
from pathlib import Path

import connexion
from dotenv import load_dotenv

from swagger_server import encoder
from .db import db

# load environment variables
env_path = Path('../../') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)

formatter = Formatter(  # pylint: disable=invalid-name
    '%(asctime)s %(levelname)s %(process)d ---- %(threadName)s  '
    '%(module)s : %(funcName)s {%(pathname)s:%(lineno)d} %(message)s', '%Y-%m-%dT%H:%M:%SZ')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

connex_app = connexion.App(__name__, specification_dir='./swagger/')
connex_app.app.json_encoder = encoder.JSONEncoder
connex_app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry API'}, pythonic_params=True)

app = connex_app.app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    os.getenv('POSTGRES_USER'),
    os.getenv('POSTGRES_PASSWORD'),
    os.getenv('POSTGRES_SERVER'),
    os.getenv('POSTGRES_PORT'),
    os.getenv('POSTGRES_DB')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
