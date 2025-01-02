from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
# Load environment variables from .env file
load_dotenv()

# Retrieve the variables
DATABASE_HOSTNAME = os.getenv("DATABASE_HOSTNAME")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")

# Create the database URL
DATABASE_URL = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create the database engine
engine = create_engine(DATABASE_URL)

#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://appuser:Reypoeta369@localhost:3306/cybertech'

#engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db