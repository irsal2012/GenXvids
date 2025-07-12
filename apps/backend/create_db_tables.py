#!/usr/bin/env python3
"""
Script to create database tables
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import create_tables
from app.models import User, Asset, Video  # Import all models to register them

def main():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        create_tables()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
