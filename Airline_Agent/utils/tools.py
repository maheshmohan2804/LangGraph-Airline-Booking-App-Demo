import json
import sys
import os
# Add parent directory to path to access Data folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.tools import tool
from Data.database import (
    query_flight,
    query_flights_departure,
    query_flights_arrival,
    query_flights_date_location,
    query_hotels_location,
    query_hotels_location_price,
    add_customer,
    add_flight_to_customer,
    add_hotel_to_customer,
    db
)

# ==================== Flight Tools ====================

@tool
def get_flight_details(flight_id: str) -> str:
    """Get flight details for a given flight ID.
    Args:
        flight_id: Flight ID for the flight
    Returns:
        JSON string with flight details or error message
    """
    flight = query_flight(flight_id)
    if flight:
        return json.dumps(flight)
    else:
        return "Flight not found."

@tool
def get_flights_by_departure(departure_airport: str) -> str:
    """Get all flights departing from a specific airport.
    Args:
        departure_airport: Airport code (e.g., JFK, LAX, ORD)
    Returns:
        JSON string with list of flights
    """
    departure_airport = departure_airport.upper()
    flights = query_flights_departure(departure_airport)
    return json.dumps(flights)

@tool
def get_flights_by_arrival(arrival_airport: str) -> str:
    """Get all flights arriving at a specific airport.
    Args:
        arrival_airport: Airport code (e.g., JFK, LAX, ORD)
    Returns:
        JSON string with list of flights
    """
    arrival_airport = arrival_airport.upper()
    flights = query_flights_arrival(arrival_airport)
    return json.dumps(flights)

@tool
def get_flights_by_date_and_departure(departure_airport: str, departure_date: str) -> str:
    """Get all flights departing from a specific airport on a specific date.
    Args:
        departure_airport: Airport code (e.g., JFK, LAX, ORD)
        departure_date: Date in format YYYY-MM-DD (e.g., 2023-10-15)
    Returns:
        JSON string with list of flights
    """
    departure_airport = departure_airport.upper()
    flights = query_flights_date_location(departure_airport, departure_date)
    return json.dumps(flights)

# ==================== Hotel Tools ====================

@tool
def get_hotel_details(hotel_id: str) -> str:
    """Get hotel details for a given hotel ID.
    Args:
        hotel_id: Hotel ID
    Returns:
        JSON string with hotel details or error message
    """
    hotels = db.get_all_hotels()
    hotel = next((h for h in hotels if h["hotel_id"] == hotel_id), None)
    if hotel:
        return json.dumps(hotel)
    else:
        return "Hotel not found."

@tool
def get_hotels_by_location(location: str) -> str:
    """Get all hotels in a specific location.
    Args:
        location: City or location name (e.g., New York, Chicago)
    Returns:
        JSON string with list of hotels
    """
    hotels = query_hotels_location(location)
    return json.dumps(hotels)

@tool
def get_hotels_by_location_and_price(location: str, min_price: float, max_price: float) -> str:
    """Get all hotels in a specific location within a price range.
    Args:
        location: City or location name (e.g., New York, Chicago)
        min_price: Minimum price per night
        max_price: Maximum price per night
    Returns:
        JSON string with list of hotels
    """
    hotels = query_hotels_location_price(location, min_price, max_price)
    return json.dumps(hotels)

# ==================== Customer Tools ====================

@tool
def get_customer_details(customer_id: str) -> str:
    """Get customer details for a given customer ID.
    Args:
        customer_id: Customer ID
    Returns:
        JSON string with customer details or error message
    """
    customer = db.get_customer(customer_id)
    if customer:
        return json.dumps(customer)
    else:
        return "Customer not found."

@tool
def create_customer(customer_id: str, flight_id: str = None, hotel_id: str = None) -> str:
    """Create a new customer with optional flight and hotel bookings.
    Args:
        customer_id: Unique customer ID
        flight_id: Optional flight ID for booking
        hotel_id: Optional hotel ID for booking
    Returns:
        Success or error message
    """
    success = add_customer(customer_id, flight_id, hotel_id)
    if success:
        return f"Customer {customer_id} created successfully."
    else:
        return f"Failed to create customer {customer_id}. Customer may already exist."

@tool
def book_flight_for_customer(customer_id: str, flight_id: str) -> str:
    """Book a flight for an existing customer.
    Args:
        customer_id: Customer ID
        flight_id: Flight ID to book
    Returns:
        Success or error message
    """
    success = add_flight_to_customer(customer_id, flight_id)
    if success:
        return f"Flight {flight_id} booked for customer {customer_id}."
    else:
        return f"Failed to book flight. Customer {customer_id} may not exist."

@tool
def book_hotel_for_customer(customer_id: str, hotel_id: str) -> str:
    """Book a hotel for an existing customer.
    Args:
        customer_id: Customer ID
        hotel_id: Hotel ID to book
    Returns:
        Success or error message
    """
    success = add_hotel_to_customer(customer_id, hotel_id)
    if success:
        return f"Hotel {hotel_id} booked for customer {customer_id}."
    else:
        return f"Failed to book hotel. Customer {customer_id} may not exist."

# ==================== Backward Compatibility Aliases ====================

# Alias for backward compatibility with existing code
get_all_flights = get_flights_by_departure
get_all_hotels = get_hotels_by_location