"""
Configuration file
"""

from os import environ, path

basedir = path.abspath(path.dirname(__file__))

class Config:
    """
    Base configuration
    """
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
    'sqlite:///' + path.join(basedir, 'db.sqlite3')
    SECRET_KEY = environ.get("SECRET_KEY") or "a-random-str1ng-spagghetified"