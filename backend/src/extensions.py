from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flasgger import Swagger


db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(async_mode="threading")
swagger = Swagger()
