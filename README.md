# Airline and Hotel Booking Agent

An intelligent conversational AI agent built with LangChain and LangGraph that helps users book flights and hotels, retrieve booking details, and manage their travel reservations through natural language interactions.

## Features

- **Multi-Agent Architecture**: Specialized agents for flight bookings, hotel bookings, and customer support
- **Intent Detection**: Automatically detects user intent and routes to the appropriate agent
- **Natural Language Processing**: Powered by Groq's LLama 3.3 70B model for understanding user queries
- **SQLite Database**: Persistent storage for customers, flights, and hotels
- **Conversational Interface**: Interactive CLI-based chat interface
- **Smart Booking**: Book flights and hotels with context-aware recommendations

## Architecture

The agent uses a graph-based workflow with the following components:

- **Intent Detection Node**: Analyzes user messages to determine their intent
- **Flight Agent**: Handles all flight-related queries and bookings
- **Hotel Agent**: Manages hotel searches and reservations
- **Customer Lookup**: Retrieves customer information and booking history
- **Disambiguation**: Clarifies ambiguous user requests

## Database Schema

### Customers Table
- `customer_id` (TEXT, PRIMARY KEY)
- `flight_id` (TEXT, NULLABLE)
- `hotel_id` (TEXT, NULLABLE)

### Flights Table
- `flight_id` (TEXT, PRIMARY KEY)
- `departure_airport` (TEXT)
- `arrival_airport` (TEXT)
- `departure_time` (TEXT)
- `arrival_time` (TEXT)

### Hotels Table
- `hotel_id` (TEXT, PRIMARY KEY)
- `name` (TEXT)
- `location` (TEXT)
- `price_per_night` (REAL)

## Prerequisites

- Python 3.8 or higher
- Groq API key (get one from [Groq Console](https://console.groq.com/))

## Installation

1. **Clone or download the project**:
   ```bash
   cd "c:\Users\madha\OneDrive\Documents\Airline and Hotel Booking Agent Lang"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   Create or update the `.env` file in the `Airline_Agent` folder:
   ```env
   GROQ_KEY="your-groq-api-key-here"
   GROQ_MODEL="llama-3.3-70b-versatile"
   ```

4. **Initialize the database**:
   ```bash
   python Data/initialize_database.py
   ```

   This will create the SQLite database and populate it with sample flight and hotel data.

## Running the Agent

1. **Start the conversational agent**:
   ```bash
   cd Airline_Agent
   python agent.py
   ```

2. **Interact with the agent**:
   - The agent will first ask for your Customer ID
   - Use one of the sample customer IDs: `CUST123`, `CUST456`, `CUST789`
   - Then you can ask questions or make requests in natural language

3. **Exit the conversation**:
   - Type `quit` or `end` to exit

## Example Usage

```
Welcome to Airline & Hotel Booking Support Agent!
============================================================

I can help you with:
  - Flight bookings and details
  - Hotel bookings and details
  - Customer support inquiries

Type 'quit' or 'end' to exit the chat.

------------------------------------------------------------

Agent: Hello! To get started, please provide your Customer ID.
You: CUST123

Agent: Customer ID set successfully! How can I assist you today?
------------------------------------------------------------

You: Show me my flight details

Agent: Your flight FLIGHT101 departs from JFK at 08:00 AM and arrives at LAX at 11:30 AM.
------------------------------------------------------------

You: I want to see hotels in New York

Agent: Here are the hotels available in New York:
- HOTEL456: Luxury Suites - $250.0 per night
- HOTEL699: Luxury Suites 2 - $255.0 per night
- HOTEL619: Luxury Suites 3 - $240.0 per night
------------------------------------------------------------

You: Book HOTEL619 for me

Agent: Successfully booked hotel HOTEL619 for customer CUST123!
------------------------------------------------------------

You: quit

Agent: Thank you for using our service. Goodbye!
```

## Available Intents

The agent can handle the following types of requests:

- **set_state_variables**: Set customer ID
- **my_flight_details**: Get your current flight details
- **all_flight_details**: Search flights by departure airport
- **book_flight**: Book a specific flight
- **my_hotel_details**: Get your current hotel details
- **all_hotel_details**: Search hotels by location
- **book_hotel**: Book a specific hotel
- **customer_support_help**: General support inquiries
- **disambiguation**: Handle unclear requests

## Sample Data

### Airports
- JFK (New York)
- LAX (Los Angeles)
- ORD (Chicago)
- SFO (San Francisco)

### Locations
- New York
- Chicago
- San Francisco

### Customer IDs
- CUST123
- CUST456
- CUST789

## Testing

Run the database tests to verify functionality:
```bash
python Data/test_database.py
```

This will test:
- Customer creation and retrieval
- Flight queries (by ID, departure, arrival, date)
- Hotel queries (by location, price range)
- Booking operations

## Technology Stack

- **LangChain**: Framework for building LLM applications
- **LangGraph**: State graph orchestration for multi-agent workflows
- **Groq**: Fast LLM inference with LLama 3.3 70B model
- **SQLite**: Lightweight database for data persistence
- **Python-dotenv**: Environment variable management

## Troubleshooting

### Database Locked Error
If you encounter a "database is locked" error, ensure that:
- No other processes are accessing the database
- The database file has proper permissions
- Run the initialize script again if needed

### API Key Issues
If you get authentication errors:
- Verify your GROQ_KEY in the `.env` file
- Ensure the key is properly quoted
- Check that the key is valid at [Groq Console](https://console.groq.com/)

### Import Errors
If you get import errors:
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're in the correct directory when running the agent

## Future Enhancements

- Web interface using Flask or Streamlit
- Support for date-based flight searches
- Price comparison and recommendations
- Multi-city trip planning
- Email confirmation for bookings
- Integration with real flight and hotel APIs

## License

This project is for educational and demonstration purposes.

## Contact

For issues or questions, please refer to the project documentation or contact the development team.
