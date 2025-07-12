#!/usr/bin/env python3
"""
Script to drop and recreate database tables
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import sync_engine, Base
from app.models import User, Asset, Video  # Import all models to register them

def main():
    """Drop and recreate all database tables"""
    try:
        print("Dropping all database tables...")
        Base.metadata.drop_all(bind=sync_engine)
        print("Creating database tables...")
        Base.metadata.create_all(bind=sync_engine)
        print("Database tables recreated successfully!")
    except Exception as e:
        print(f"Error recreating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
