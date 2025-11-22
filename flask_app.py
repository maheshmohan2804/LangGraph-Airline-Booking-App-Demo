from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
import sys
import os

# Add Airline_Agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Airline_Agent'))

from utils.state import create_support_graph

app = Flask(__name__)
CORS(app)

# Initialize the agent graph
agent_graph = create_support_graph()

# Store session states (in production, use Redis or database)
sessions = {}


def get_initial_state():
    """Create initial state for a new session."""
    return {
        "messages": [],
        "customer_id": "",
        "ticket_id": "",
        "hotel_id": "",
        "intent": "",
        "tools": [],
        "issue_type": "",
        "resolution_status": "pending",
        "next": ""
    }


@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a new conversation session."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        # Initialize new session state
        sessions[session_id] = get_initial_state()

        return jsonify({
            'status': 'success',
            'message': 'Session started successfully',
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/end_session', methods=['POST'])
def end_session():
    """End a conversation session."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        # Clear session state
        if session_id in sessions:
            del sessions[session_id]

        return jsonify({
            'status': 'success',
            'message': 'Session ended successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message."""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        print(f"\n[DEBUG] Received message: {user_message}")
        print(f"[DEBUG] Session ID: {session_id}")

        # Get or create session state
        if session_id not in sessions:
            sessions[session_id] = get_initial_state()
            print(f"[DEBUG] Created new session: {session_id}")

        state = sessions[session_id]
        print(f"[DEBUG] Current state messages count: {len(state['messages'])}")

        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        state["intent"] = ""
        state["next"] = ""

        print(f"[DEBUG] Invoking agent graph...")
        # Invoke the agent
        result = agent_graph.invoke(state)
        sessions[session_id] = result

        print(f"[DEBUG] Agent completed. Total messages: {len(result['messages'])}")

        # Get the last AI message
        last_message = result["messages"][-1]
        if hasattr(last_message, 'content'):
            response = last_message.content
        else:
            response = str(last_message)

        print(f"[DEBUG] Response: {response[:100]}...")

        return jsonify({
            'status': 'success',
            'response': response,
            'customer_id': result.get('customer_id', ''),
            'intent': result.get('intent', '')
        })
    except Exception as e:
        print(f"[ERROR] Exception in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error processing message: {str(e)}'
        }), 500


@app.route('/api/get_state', methods=['POST'])
def get_state():
    """Get current session state."""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        if session_id not in sessions:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404

        state = sessions[session_id]
        return jsonify({
            'status': 'success',
            'customer_id': state.get('customer_id', ''),
            'intent': state.get('intent', ''),
            'resolution_status': state.get('resolution_status', 'pending')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Airline & Hotel Booking Agent API'
    })


if __name__ == '__main__':
    print("Starting Airline & Hotel Booking Agent API...")
    print("API will be available at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)