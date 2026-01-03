import os

class Config:
    # IMPORTANT: Change this to a real, random secret key in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False