# database.py
# Handles database connection and session management

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL — file will be created automatically on first run
DATABASE_URL = "sqlite:///./students.db"

# Create the SQLAlchemy engine
# check_same_thread=False is required for SQLite to work with FastAPI's async nature
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all ORM models will inherit from
Base = declarative_base()


# Dependency injection function — used in route handlers via FastAPI's Depends()
def get_db():
    """
    Yields a database session and ensures it is closed after the request,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
