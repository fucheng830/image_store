# init_db.py
import load_env
import os
from models import Base
from database import engine


def create_tables():
    # Create tables defined in your models
    Base.metadata.drop_all(bind=engine)  # Drops all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()

