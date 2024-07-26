"""
This module contains functions for interacting with the database.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def check_db_connection():
    """
    Check the connection to the database.

    This function attempts to establish a connection to the database using the configured
    SQLAlchemy engine. It executes a simple SQL query to check if the connection is successful.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        with engine.connect() as db:
            db.execute(text("SELECT 1"))
            return True
    except OperationalError:
        return False


def get_db():
    """
    Get a database session.

    This function returns a session object that can be used to interact with the database.
    The session is created using the SessionLocal object, which is a session factory
    configured with the SQLAlchemy engine.

    Yields:
        SessionLocal: A session object for interacting with the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
