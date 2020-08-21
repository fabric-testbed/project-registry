#!/usr/bin/env python3

import connexion
from swagger_server import encoder

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'FABRIC Project Registry'}, pythonic_params=True)
