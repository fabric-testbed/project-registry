#!/usr/bin/env python3

import connexion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from swagger_server import encoder

from .config import config

CONFIG_FILE = 'swagger_server/ini/pr_database.ini'
CONFIG_SECTION = 'postgres'

params = config(filename=CONFIG_FILE, section=CONFIG_SECTION)

POSTGRES_ENGINE = 'postgres://' + params['user'] + ':' + params['password'] \
                  + '@' + params['host'] + ':' + params['port'] \
                  + '/' + params['database']

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry'}, pythonic_params=True)

# Setup COmanage LDAP connection
CONFIG_FILE = 'swagger_server/ini/pr_comanage.ini'
CONFIG_SECTION = 'ldap'

LDAP_PARAMS = config(filename=CONFIG_FILE, section=CONFIG_SECTION)
