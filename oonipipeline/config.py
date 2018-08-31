import os


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'postgresql://steve:thisisanewpassword@localhost:5432/pipeline'
SQLALCHEMY_BINDS = {'metadb': 'postgresql://steve:thisisanewpassword@localhost:5432/metadb'}
UPLOAD_PATH = os.environ['HOME']
