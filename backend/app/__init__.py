from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt, api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Needs to be called before registering namespaces
    api.init_app(app)
    
    # Register namespaces
    from .auth.views import auth_ns
    from .users.views import users_ns
    from .jobs.views import jobs_ns
    from .applications.views import applications_ns
    from .reviews.views import reviews_ns
    
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(jobs_ns, path='/api/v1/jobs')
    api.add_namespace(applications_ns, path='/api/v1/applications')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    
    return app
