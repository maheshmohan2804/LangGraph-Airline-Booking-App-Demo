# Airline & Hotel Booking Agent - Deployment Guide

This guide explains how to run the Airline & Hotel Booking Agent with a Flask API backend and Streamlit UI frontend.

## Architecture

- **flask_app.py**: Flask REST API that runs the LangGraph agent
- **Airline_Agent_UI.py**: Streamlit web interface for users to interact with the agent
- **Airline_Agent/**: Core agent logic and utilities

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up Environment Variables**

Make sure your `.env` file in the `Airline_Agent/` folder contains the necessary API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Running the Application

You need to run both the Flask API and Streamlit UI in separate terminals.

### Option 1: Run in Separate Terminals

**Terminal 1 - Start Flask API:**

```bash
python flask_app.py
```

The API will start at `http://localhost:5000`

**Terminal 2 - Start Streamlit UI:**

```bash
streamlit run Airline_Agent_UI.py
```

The UI will open in your browser at `http://localhost:8501`

### Option 2: Run with Background Process (Windows)

**Start Flask API in background:**

```bash
start python flask_app.py
```

**Start Streamlit UI:**

```bash
streamlit run Airline_Agent_UI.py
```

## Using the Application

1. **Start the Streamlit UI** - The interface will open in your browser
2. **Check API Status** - The sidebar shows if the Flask API is connected (green dot)
3. **Click "Start"** - Begin a new conversation
4. **Provide Customer ID** - Enter your customer ID when prompted
5. **Chat with the Agent** - Ask about flights, hotels, or bookings
6. **Click "End"** - Finish the conversation when done

## Features

### Streamlit UI Features:
- Clean white background design
- Real-time chat interface
- Start/End conversation buttons in sidebar
- API connection status indicator
- Session information display
- Timestamp for each message
- Visual distinction between user and assistant messages

### Flask API Endpoints:

- `GET /api/health` - Check API health status
- `POST /api/start_session` - Start a new conversation session
- `POST /api/end_session` - End a conversation session
- `POST /api/chat` - Send a message and get a response
- `POST /api/get_state` - Get current session state

## API Usage Examples

### Start Session
```bash
curl -X POST http://localhost:5000/api/start_session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user123"}'
```

### Send Message
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user123", "message": "Show me available flights"}'
```

### End Session
```bash
curl -X POST http://localhost:5000/api/end_session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user123"}'
```

## Troubleshooting

### API Not Connected
- Ensure `flask_app.py` is running in a separate terminal
- Check that port 5000 is not blocked by firewall
- Verify the API is accessible at `http://localhost:5000/api/health`

### Streamlit Won't Start
- Check if port 8501 is available
- Try running with: `streamlit run Airline_Agent_UI.py --server.port 8502`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're in the correct directory

### Agent Not Responding
- Check the Flask terminal for error messages
- Verify your GROQ_API_KEY is set correctly in the `.env` file
- Check your internet connection for API calls

## File Structure

```
Airline and Hotel Booking Agent Lang/
├── flask_app.py              # Flask API backend
├── Airline_Agent_UI.py       # Streamlit frontend
├── requirements.txt          # Python dependencies
├── README_DEPLOYMENT.md      # This file
├── Airline_Agent/            # Agent core logic
│   ├── agent.py             # Original CLI agent
│   ├── utils/               # Agent utilities
│   │   ├── state.py         # State graph definition
│   │   └── nodes.py         # Agent nodes
│   └── .env                 # Environment variables
└── Data/                     # Data files
```

## Notes

- Each user session is tracked independently using session IDs
- In production, consider using Redis or a database instead of in-memory session storage
- The Flask API runs in debug mode by default - disable for production
- CORS is enabled for development - configure appropriately for production

## Support

For issues or questions about:
- **Flight bookings**: The agent can search, view, and book flights
- **Hotel bookings**: The agent can search, view, and book hotels
- **Customer support**: Lookup customer information and booking details
