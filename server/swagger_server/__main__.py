from flask_migrate import Migrate

from swagger_server.db import db
from swagger_server import app


def create_app():
    db.init_app(app)
    return app


flask_app = create_app()
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    logger = flask_app.logger
    logger.info("Starting FABRIC Project Registry API")
    flask_app.run()
