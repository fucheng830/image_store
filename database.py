# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# SQLALCHEMY_DATABASE_URL should be in the format:
# dialect+driver://username:password@host:port/database
# For a simple PostgreSQL connection, it might look like this:
SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]

# Create an engine
# echo=True will print all the SQL statements, which is useful for debugging.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False,
)

# Each instance of the SessionLocal class will be a database session. 
# The class itself is not a database session yet.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise 
    finally:
        db.close()





