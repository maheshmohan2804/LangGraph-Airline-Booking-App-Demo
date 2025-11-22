"""
Script to initialize the database with all data
Run this once to set up the database with flights, hotels, and customers
"""

import os
import sys

# Delete old database if it exists
db_path = os.path.join(os.path.dirname(__file__), "booking_system.db")
if os.path.exists(db_path):
    print("Removing old database...")
    os.remove(db_path)
    # Also remove WAL files if they exist
    for ext in ['-shm', '-wal']:
        wal_file = db_path + ext
        if os.path.exists(wal_file):
            os.remove(wal_file)

# Import database module (this will create tables)
from database import db

# Load flights and hotels
print("\nInitializing database with flight and hotel data...")
result = db.load_initial_data()
print(f"Loaded {result['flights_loaded']} flights and {result['hotels_loaded']} hotels")

# Load customers
from customer_data import load_customer_data
customer_count = load_customer_data()

print(f"\n{'='*60}")
print("Database initialization complete!")
print(f"{'='*60}")
print(f"Total flights: {len(db.get_all_flights())}")
print(f"Total hotels: {len(db.get_all_hotels())}")
print(f"Total customers: {customer_count}")
print(f"{'='*60}\n")
