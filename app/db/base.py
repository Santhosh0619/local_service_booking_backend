from sqlalchemy.orm import declarative_base

# All of our database models (like User, Booking) will inherit from this Base class.
# This tells SQLAlchemy how to map our Python classes to MySQL tables.
Base = declarative_base()
