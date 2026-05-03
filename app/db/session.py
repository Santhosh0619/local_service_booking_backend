from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 1. Create the "engine" which is the actual connection to the MySQL database
engine = create_engine(settings.DATABASE_URL)

# 2. Create a factory for database sessions. We set autocommit=False so we can 
# manually commit transactions safely.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. A dependency function. Every time an API endpoint needs to talk to the database,
# it will call this function to get an open connection, and then safely close it after.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
