import os
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False # silence the deprecation warning
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')   
