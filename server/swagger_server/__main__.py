#!/usr/bin/env python3

import os

import connexion
from flask_migrate import Migrate

from swagger_server import encoder
from .db import db

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

db.init_app(app)
migrate = Migrate(app, db)

logger = app.logger


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    logger.info("Starting FABRIC Project Registry API")
    app.run(port=5000, debug=True)
