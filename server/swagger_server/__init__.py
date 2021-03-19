#!/usr/bin/env python3

from configparser import ConfigParser

import connexion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import encoder

config = ConfigParser()
config.read('swagger_server/config/config.ini')

POSTGRES_ENGINE = 'postgres://' + config.get('postgres', 'user') + ':' + config.get('postgres', 'password') \
                  + '@' + config.get('postgres', 'host') + ':' + config.get('postgres', 'port') \
                  + '/' + config.get('postgres', 'database')

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry'}, pythonic_params=True)
