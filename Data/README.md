# Database System Documentation

## Overview
This database system manages airline and hotel bookings with three separate tables: customers, flights, and hotels.

## Database Structure

### 1. **Customers Table**
- `customer_id` (PRIMARY KEY)
- `flight_id`
- `hotel_id`

### 2. **Flights Table**
- `flight_id` (PRIMARY KEY)
- `departure_airport`
- `arrival_airport`
- `departure_time`
- `arrival_time`

### 3. **Hotels Table**
- `hotel_id` (PRIMARY KEY)
- `name`
- `location`
- `price_per_night`

## Getting Started

### Initialize the Database
Run this command **once** to set up the database with all initial data:
```bash
python initialize_database.py
```

This will:
- Create the database file `booking_system.db`
- Load all flights from `flight_data.py`
- Load all hotels from `hotel_data.py`
- Load all customers from `customer_data.py`

### Test the Database
```bash
python test_database.py
```

## Available Functions

### Customer Management

```python
from database import add_customer, add_flight_to_customer, add_hotel_to_customer

# Add a new customer
add_customer("CUST001", flight_id="FLIGHT123", hotel_id="HOTEL456")

# Add flight to existing customer
add_flight_to_customer("CUST001", "FLIGHT789")

# Add hotel to existing customer
add_hotel_to_customer("CUST001", "HOTEL123")
```

### Flight Queries

```python
from database import (
    query_flight,
    query_flights_departure,
    query_flights_arrival,
    query_flights_date_location
)

# Query flight by ID
flight = query_flight("FLIGHT123")

# Query all flights from a location
flights = query_flights_departure("JFK")

# Query all flights to a location
flights = query_flights_arrival("LAX")

# Query flights by date and departure location
flights = query_flights_date_location("JFK", "2023-10-15")
```

### Hotel Queries

```python
from database import query_hotels_location, query_hotels_location_price

# Query hotels by location
hotels = query_hotels_location("New York")

# Query hotels by location and price range
hotels = query_hotels_location_price("New York", 200.0, 300.0)
```

## Direct Database Access

For advanced operations:

```python
from database import db

# Get all flights
all_flights = db.get_all_flights()

# Get all hotels
all_hotels = db.get_all_hotels()

# Get customer by ID
customer = db.get_customer("CUST001")
```

## Example Usage

```python
from database import *

# Add a new customer with a flight
add_customer("CUST100", flight_id="FLIGHT123")

# Find all flights from LAX
lax_flights = query_flights_departure("LAX")
for flight in lax_flights:
    print(f"{flight['flight_id']}: {flight['departure_airport']} -> {flight['arrival_airport']}")

# Find affordable hotels in New York (under $260/night)
hotels = query_hotels_location_price("New York", 0, 260)
for hotel in hotels:
    print(f"{hotel['name']}: ${hotel['price_per_night']}/night")
```

## Files

- `database.py` - Main database module with all functionality
- `initialize_database.py` - One-time setup script
- `test_database.py` - Test script demonstrating all features
- `flight_data.py` - Initial flight data
- `hotel_data.py` - Initial hotel data
- `customer_data.py` - Initial customer data
- `booking_system.db` - SQLite database file (created automatically)
