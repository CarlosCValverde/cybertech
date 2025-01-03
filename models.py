from flask import g
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

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

SessionLocal = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(32), unique=True, nullable=False)
    username = Column(String(32), nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    projects = relationship('Project', backref='users', lazy='dynamic')


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, nullable=False)
    p_type = Column(Enum('dwp', 'sce'), nullable=False)
    po_number = Column(String(32), unique=True, nullable=False)
    address = Column(String(64), unique=True, nullable=False)
    num_chargers = Column(Integer)
    permit_num = Column(String(64))
    project_status = Column(Enum('active', 'completed', 'on_hold'), nullable=False)
    start_date = Column(Date)
    invoice = Column(Enum('50%', '90%', '100%'), nullable=False)
    datto = Column(Enum('completed', 'partial', 'empty'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    inspections = relationship('Inspection', backref='projects', lazy='dynamic')


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, nullable=False)
    i_type = Column(Enum('underground', 'rough', 'power_release', 'final', 'pending'), nullable=False)
    inspection_status = Column(Enum('passed', 'rescheduled', 'pending'), nullable=False)
    inspection_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)


class CompositeKey(Base):
    __tablename__ = 'compositekeys'

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)


Base.metadata.create_all(bind=engine)