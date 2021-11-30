from flask_migrate import Migrate

from swagger_server.db import db
from . import app


@app.before_first_request
def create_tables():
    db.create_all()


def create_app():
    db.init_app(app)
    return app


if __name__ == '__main__':
    flask_app = create_app()
    migrate = Migrate(app, db)
    logger = flask_app.logger
    logger.info("Starting FABRIC Project Registry API")
    flask_app.run(port=6000, debug=True)
