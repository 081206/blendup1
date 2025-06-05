from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    language = db.Column(db.String(10), default='en')
    theme = db.Column(db.String(10), default='light')
    is_private = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(32), nullable=True)
    interests = db.Column(db.Text, nullable=True)  # Store interests as comma-separated values
    
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

class User(db.Model):
    __tablename__ = 'user'  # Explicitly set table name
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)  # Store the file path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    suspended = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    __tablename__ = 'report'  # Explicitly set table name
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reported_user_id = db.Column(db.Integer, nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', backref='reports_made')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

# New model for blocked users
class BlockedUser(db.Model):
    __tablename__ = 'blocked_user'
    
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    blocker = db.relationship('User', foreign_keys=[blocker_id], backref='blocked_users')
    blocked = db.relationship('User', foreign_keys=[blocked_id], backref='blocked_by_users')
    
    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),
    )
