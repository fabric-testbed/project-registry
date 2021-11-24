#!/usr/bin/env python3

from pathlib import Path

from dotenv import load_dotenv
from logging.config import dictConfig

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

# load environment variables
env_path = Path('../../') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)


# from configparser import ConfigParser
#
# # import connexion
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from . import encoder
#
# config = ConfigParser()
# config.read('server/swagger_server/config/config.ini')
#
# POSTGRES_ENGINE = 'postgres://' + config.get('postgres', 'user') + ':' + config.get('postgres', 'password') \
#                   + '@' + config.get('postgres', 'host') + ':' + config.get('postgres', 'port') \
#                   + '/' + config.get('postgres', 'database')
#
# engine = create_engine(POSTGRES_ENGINE)
# Session = sessionmaker(bind=engine)
# Session = sessionmaker()
#
# app = connexion.App(__name__, specification_dir='./swagger/')
# app.app.json_encoder = encoder.JSONEncoder
# app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry'}, pythonic_params=True)
