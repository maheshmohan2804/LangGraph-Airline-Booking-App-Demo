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

## Project Structure

```
Airline and Hotel Booking Agent Lang/

