import logging
import sys
from flask import Flask
from .settings import AppConfig
from .extensions import db, jwt, socketio, swagger
from .cache import cache
from .log.models import Log
from .register_blueprints import register_blueprints


def create_app(config_object: type[AppConfig] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or AppConfig())
    
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    if not app_logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(formatter)
        app_logger.addHandler(console_handler)
        app_logger.propagate = False

    db.init_app(app)
    jwt.init_app(app)
    if not app.config.get("TESTING"):
        cache.init_app(app)
    swagger.init_app(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    socketio.init_app(app, cors_allowed_origins="*")
    return app
