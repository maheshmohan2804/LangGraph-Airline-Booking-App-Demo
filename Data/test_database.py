"""
Test script to demonstrate all database functionality
"""

from database import (
    add_customer,
    add_flight_to_customer,
    add_hotel_to_customer,
    query_flight,
    query_flights_departure,
    query_flights_arrival,
    query_flights_date_location,
    query_hotels_location,
    query_hotels_location_price,
    db
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_customer_functions():
    """Test customer-related functions"""
    print_section("Testing Customer Functions")

    # Add a new customer
    print("\n1. Adding new customer 'CUST999'...")
    success = add_customer("CUST999")
    print(f"   Result: {'Success' if success else 'Failed'}")

    # Add flight to customer
    print("\n2. Adding flight 'FLIGHT123' to customer 'CUST999'...")
    success = add_flight_to_customer("CUST999", "FLIGHT123")
    print(f"   Result: {'Success' if success else 'Failed'}")

    # Add hotel to customer
    print("\n3. Adding hotel 'HOTEL456' to customer 'CUST999'...")
    success = add_hotel_to_customer("CUST999", "HOTEL456")
    print(f"   Result: {'Success' if success else 'Failed'}")

    # Verify customer
    print("\n4. Verifying customer 'CUST999'...")
    customer = db.get_customer("CUST999")
    if customer:
        print(f"   Customer ID: {customer['customer_id']}")
        print(f"   Flight ID: {customer['flight_id']}")
        print(f"   Hotel ID: {customer['hotel_id']}")
    else:
        print("   Customer not found")


def test_flight_queries():
    """Test flight query functions"""
    print_section("Testing Flight Query Functions")

    # Query flight by ID
    print("\n1. Query flight by ID 'FLIGHT123'...")
    flight = query_flight("FLIGHT123")
    if flight:
        print(f"   Flight ID: {flight['flight_id']}")
        print(f"   From: {flight['departure_airport']} -> To: {flight['arrival_airport']}")
        print(f"   Departure: {flight['departure_time']}")
        print(f"   Arrival: {flight['arrival_time']}")
    else:
        print("   Flight not found")

    # Query flights by departure location
    print("\n2. Query all flights departing from 'LAX'...")
    flights = query_flights_departure("LAX")
    print(f"   Found {len(flights)} flight(s):")
    for flight in flights:
        print(f"   - {flight['flight_id']}: {flight['departure_airport']} -> {flight['arrival_airport']}")

    # Query flights by arrival location
    print("\n3. Query all flights arriving at 'SFO'...")
    flights = query_flights_arrival("SFO")
    print(f"   Found {len(flights)} flight(s):")
    for flight in flights:
        print(f"   - {flight['flight_id']}: {flight['departure_airport']} -> {flight['arrival_airport']}")

    # Query flights by departure date and location
    print("\n4. Query flights departing from 'JFK' on '2023-10-15'...")
    flights = query_flights_date_location("JFK", "2023-10-15")
    print(f"   Found {len(flights)} flight(s):")
    for flight in flights:
        print(f"   - {flight['flight_id']}: Departs at {flight['departure_time']}")


def test_hotel_queries():
    """Test hotel query functions"""
    print_section("Testing Hotel Query Functions")

    # Query hotels by location
    print("\n1. Query all hotels in 'New York'...")
    hotels = query_hotels_location("New York")
    print(f"   Found {len(hotels)} hotel(s):")
    for hotel in hotels:
        print(f"   - {hotel['hotel_id']}: {hotel['name']} - ${hotel['price_per_night']}/night")

    # Query hotels by location and price range
    print("\n2. Query hotels in 'New York' with price range $240-$250...")
    hotels = query_hotels_location_price("New York", 240.0, 250.0)
    print(f"   Found {len(hotels)} hotel(s):")
    for hotel in hotels:
        print(f"   - {hotel['hotel_id']}: {hotel['name']} - ${hotel['price_per_night']}/night")


def show_all_data():
    """Show all data in the database"""
    print_section("Database Contents")

    print("\nAll Flights:")
    flights = db.get_all_flights()
    for flight in flights:
        print(f"  {flight['flight_id']}: {flight['departure_airport']} -> {flight['arrival_airport']}")

    print("\nAll Hotels:")
    hotels = db.get_all_hotels()
    for hotel in hotels:
        print(f"  {hotel['hotel_id']}: {hotel['name']} in {hotel['location']} (${hotel['price_per_night']}/night)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DATABASE FUNCTIONALITY TEST")
    print("=" * 60)

    # Show initial data
    show_all_data()

    # Run tests
    test_customer_functions()
    test_flight_queries()
    test_hotel_queries()

    print("\n" + "=" * 60)
    print("  All tests completed!")
    print("=" * 60 + "\n")
