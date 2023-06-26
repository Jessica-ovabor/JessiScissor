from datetime import datetime
from string import ascii_letters, digits    # for generating random string
from random import choice
from .extensions import db, login_manager
from flask_login import UserMixin     # for login_manager


class Demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demo_original_url = db.Column(db.String(1000), nullable=True)
    demo_short_url = db.Column(db.String(5), unique=True, nullable=True)
    
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     if not self.short_url:
    #         self.short_url = self.generate_short_url()
    # def generate_short_url(self):
    #     characters = ascii_letters + digits
    #     while True:
    #         short_url = ''.join(choice(characters) for i in range(5))
    #         url = self.query.filter_by(short_url=short_url).first()
    #         if url:
    #             return self.generate_short_url()
    #         return short_url
  
    def save(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(1000), nullable=False)
    short_url = db.Column(db.String(5), unique=True, nullable=True)
    custom_short_url = db.Column(db.String(5), unique=True, nullable=True) 
    custom_domain = db.Column(db.String(1000), nullable=True)   
    visits = db.Column(db.Integer, nullable=True, default=0)
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)    # user.id is the table n    
    def __repr__(self):
        return f"Url('{self.original_url}', '{self.short_url}')"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.short_url:
            self.short_url = self.generate_short_url()
    def generate_short_url(self):
        characters = ascii_letters + digits
        while True:
            short_url = ''.join(choice(characters) for i in range(5))
            url = self.query.filter_by(short_url=short_url).first()
            if url:
                return self.generate_short_url()
            return short_url
    def update_visits_count(self):
        self.visits = self.visits + 1
        db.session.commit()
    def update_custom_short_url(self, new_custom_short_url):
        self.custom_short_url = new_custom_short_url
        db.session.commit()
    def save(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True , nullable=False)    # unique=True means that no two users can have the same username
    username = db.Column(db.String(30), unique=True , nullable=False)    # unique=True means that no two users can have the same username
    password = db.Column(db.String(30),nullable=False)
    url = db.relationship('Url', backref='user',lazy=True)    # 'Url' is the table name
    def __repr__(self):
        return f"User('{self.username}')"
    def save(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))