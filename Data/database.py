import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

# Import existing data
try:
    from .flight_data import FLIGHT_DATA
    from .hotel_data import HOTEL_DATA
except ImportError:
    # Fallback for direct execution
    from flight_data import FLIGHT_DATA
    from hotel_data import HOTEL_DATA

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "booking_system.db")


class BookingDatabase:
    """SQLite database manager for airline and hotel booking system"""

    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        return conn

    def init_database(self):
        """Initialize the database and create all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Enable WAL mode for better concurrent access
        cursor.execute('PRAGMA journal_mode=WAL')

        # Set timeout for locks (10 seconds)
        conn.execute('PRAGMA busy_timeout = 10000')

        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                flight_id TEXT,
                hotel_id TEXT
            )
        ''')

        # Create flights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                flight_id TEXT PRIMARY KEY,
                departure_airport TEXT NOT NULL,
                arrival_airport TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL
            )
        ''')

        # Create hotels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotels (
                hotel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                price_per_night REAL NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def load_initial_data(self):
        """Load all existing data from flight_data.py and hotel_data.py into the database"""
        # Load flights
        flight_count = 0
        for flight in FLIGHT_DATA:
            if self.add_flight(
                flight["flight_id"],
                flight["departure_airport"],
                flight["arrival_airport"],
                flight["departure_time"],
                flight["arrival_time"]
            ):
                flight_count += 1

        # Load hotels
        hotel_count = 0
        for hotel in HOTEL_DATA:
            if self.add_hotel(
                hotel["hotel_id"],
                hotel["name"],
                hotel["location"],
                hotel["price_per_night"]
            ):
                hotel_count += 1

        return {"flights_loaded": flight_count, "hotels_loaded": hotel_count}

    # ==================== Customer Functions ====================

    def add_customer(self, customer_id: str, flight_id: str = None, hotel_id: str = None) -> bool:
        """
        Add a new customer to the database

        Args:
            customer_id: Unique customer identifier
            flight_id: Flight booking ID (optional)
            hotel_id: Hotel booking ID (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO customers (customer_id, flight_id, hotel_id)
                VALUES (?, ?, ?)
            ''', (customer_id, flight_id, hotel_id))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except Exception as e:
            print(f"Error adding customer: {e}")
            return False

    def add_flight_to_customer(self, customer_id: str, flight_id: str) -> bool:
        """
        Add a flight_id to an existing customer

        Args:
            customer_id: Customer identifier
            flight_id: Flight booking ID

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE customers
                SET flight_id = ?
                WHERE customer_id = ?
            ''', (flight_id, customer_id))

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            print(f"Error adding flight to customer: {e}")
            return False

    def add_hotel_to_customer(self, customer_id: str, hotel_id: str) -> bool:
        """
        Add a hotel_id to an existing customer

        Args:
            customer_id: Customer identifier
            hotel_id: Hotel booking ID

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE customers
                SET hotel_id = ?
                WHERE customer_id = ?
            ''', (hotel_id, customer_id))

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            print(f"Error adding hotel to customer: {e}")
            return False

    # ==================== Flight Functions ====================

    def add_flight(self, flight_id: str, departure_airport: str, arrival_airport: str,
                   departure_time: str, arrival_time: str) -> bool:
        """
        Add a new flight to the database

        Args:
            flight_id: Unique flight identifier
            departure_airport: Departure airport code
            arrival_airport: Arrival airport code
            departure_time: Departure time (format: YYYY-MM-DD HH:MM:SS)
            arrival_time: Arrival time (format: YYYY-MM-DD HH:MM:SS)

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO flights (flight_id, departure_airport, arrival_airport,
                                   departure_time, arrival_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (flight_id, departure_airport, arrival_airport, departure_time, arrival_time))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except Exception as e:
            print(f"Error adding flight: {e}")
            return False

    def query_flight_by_id(self, flight_id: str) -> Optional[Dict]:
        """
        Query flight by flight_id

        Args:
            flight_id: Flight identifier

        Returns:
            Dictionary with flight data or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT flight_id, departure_airport, arrival_airport, departure_time, arrival_time
            FROM flights
            WHERE flight_id = ?
        ''', (flight_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def query_flights_by_departure(self, departure_airport: str) -> List[Dict]:
        """
        Query all flights by departure location

        Args:
            departure_airport: Departure airport code

        Returns:
            List of dictionaries containing flight data
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT flight_id, departure_airport, arrival_airport, departure_time, arrival_time
            FROM flights
            WHERE departure_airport = ?
        ''', (departure_airport,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def query_flights_by_arrival(self, arrival_airport: str) -> List[Dict]:
        """
        Query all flights by arrival location

        Args:
            arrival_airport: Arrival airport code

        Returns:
            List of dictionaries containing flight data
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT flight_id, departure_airport, arrival_airport, departure_time, arrival_time
            FROM flights
            WHERE arrival_airport = ?
        ''', (arrival_airport,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def query_flights_by_departure_date_location(self, departure_airport: str,
                                                  departure_date: str) -> List[Dict]:
        """
        Query all flights by departure date and location

        Args:
            departure_airport: Departure airport code
            departure_date: Departure date (format: YYYY-MM-DD)

        Returns:
            List of dictionaries containing flight data
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Match flights where departure_time starts with the given date
        cursor.execute('''
            SELECT flight_id, departure_airport, arrival_airport, departure_time, arrival_time
            FROM flights
            WHERE departure_airport = ? AND departure_time LIKE ?
        ''', (departure_airport, f"{departure_date}%"))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== Hotel Functions ====================

    def add_hotel(self, hotel_id: str, name: str, location: str, price_per_night: float) -> bool:
        """
        Add a new hotel to the database

        Args:
            hotel_id: Unique hotel identifier
            name: Hotel name
            location: Hotel location/city
            price_per_night: Price per night

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO hotels (hotel_id, name, location, price_per_night)
                VALUES (?, ?, ?, ?)
            ''', (hotel_id, name, location, price_per_night))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except Exception as e:
            print(f"Error adding hotel: {e}")
            return False

    def query_hotels_by_location(self, location: str) -> List[Dict]:
        """
        Query all hotels by location

        Args:
            location: Hotel location/city

        Returns:
            List of dictionaries containing hotel data
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Use case-insensitive search
        cursor.execute('''
            SELECT hotel_id, name, location, price_per_night
            FROM hotels
            WHERE LOWER(location) = LOWER(?)
        ''', (location,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def query_hotels_by_location_price_range(self, location: str,
                                             min_price: float, max_price: float) -> List[Dict]:
        """
        Query all hotels by location and price range

        Args:
            location: Hotel location/city
            min_price: Minimum price per night
            max_price: Maximum price per night

        Returns:
            List of dictionaries containing hotel data
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Use case-insensitive search
        cursor.execute('''
            SELECT hotel_id, name, location, price_per_night
            FROM hotels
            WHERE LOWER(location) = LOWER(?) AND price_per_night BETWEEN ? AND ?
        ''', (location, min_price, max_price))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== Utility Functions ====================

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT customer_id, flight_id, hotel_id
            FROM customers
            WHERE customer_id = ?
        ''', (customer_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_flights(self) -> List[Dict]:
        """Get all flights"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT flight_id, departure_airport, arrival_airport, departure_time, arrival_time FROM flights')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_hotels(self) -> List[Dict]:
        """Get all hotels"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT hotel_id, name, location, price_per_night FROM hotels')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]


# Initialize database instance
db = BookingDatabase()


# ==================== Helper Functions for Easy Access ====================

def add_customer(customer_id: str, flight_id: str = None, hotel_id: str = None) -> bool:
    """Add a new customer"""
    return db.add_customer(customer_id, flight_id, hotel_id)

def add_flight_to_customer(customer_id: str, flight_id: str) -> bool:
    """Add flight to customer"""
    return db.add_flight_to_customer(customer_id, flight_id)

def add_hotel_to_customer(customer_id: str, hotel_id: str) -> bool:
    """Add hotel to customer"""
    return db.add_hotel_to_customer(customer_id, hotel_id)

def query_flight(flight_id: str) -> Optional[Dict]:
    """Query flight by ID"""
    return db.query_flight_by_id(flight_id)

def query_flights_departure(departure_airport: str) -> List[Dict]:
    """Query flights by departure location"""
    return db.query_flights_by_departure(departure_airport)

def query_flights_arrival(arrival_airport: str) -> List[Dict]:
    """Query flights by arrival location"""
    return db.query_flights_by_arrival(arrival_airport)

def query_flights_date_location(departure_airport: str, departure_date: str) -> List[Dict]:
    """Query flights by departure date and location"""
    return db.query_flights_by_departure_date_location(departure_airport, departure_date)

def query_hotels_location(location: str) -> List[Dict]:
    """Query hotels by location"""
    return db.query_hotels_by_location(location)

def query_hotels_location_price(location: str, min_price: float, max_price: float) -> List[Dict]:
    """Query hotels by location and price range"""
    return db.query_hotels_by_location_price_range(location, min_price, max_price)