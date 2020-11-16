#!/usr/bin/env python3

import connexion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import encoder

from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')

POSTGRES_ENGINE = 'postgres://' + config['postgres']['user'] + ':' + config['postgres']['password'] \
                  + '@' + config['postgres']['host'] + ':' + config['postgres']['port'] \
                  + '/' + config['postgres']['database']

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry'}, pythonic_params=True)
