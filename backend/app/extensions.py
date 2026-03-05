from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api(
    version='1.0',
    title='Micro Jobs API',
    description='A Micro Job Platform API',
    doc='/api/docs'
)
