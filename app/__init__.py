from flask import Flask
from .routes import cache,limiter
from .extensions import db,login_manager
from .routes import url
import os
from dotenv import load_dotenv

login_manager.login_view = 'url.login'

load_dotenv()

def create_app(config_file='settings.py'):
   app=Flask(__name__)
   app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
   app.config.from_pyfile(config_file)
   limiter.init_app(app)
   cache.init_app(app)
   db.init_app(app)
   login_manager.init_app(app)
   app.register_blueprint(url)
   with app.app_context():
      db.create_all()
   return app