# models.py
# SQLAlchemy ORM models — define the shape of database tables

from sqlalchemy import Column, Integer, String
from database import Base


class Student(Base):
    """
    ORM model for the 'students' table.
    Each attribute maps directly to a column in the SQLite database.
    """
    __tablename__ = "students"

    id     = Column(Integer, primary_key=True, index=True)          # Auto-incremented PK
    name   = Column(String, nullable=False)                          # Full name, required
    email  = Column(String, unique=True, index=True, nullable=False) # Unique email
    age    = Column(Integer, nullable=False)                         # Must be > 0 (enforced in schema)
    course = Column(String, nullable=False)                          # Enrolled course, required

    def __repr__(self):
        return f"<Student id={self.id} name={self.name!r} email={self.email!r}>"
