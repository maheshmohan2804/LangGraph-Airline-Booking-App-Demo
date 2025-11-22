import streamlit as st
import requests
import uuid
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Airline & Hotel Booking Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white background and clean design
st.markdown("""
    <style>
    .main {
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .message-content {
        color: #555;
        line-height: 1.6;
    }
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
    h1 {
        color: #1976D2;
    }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:5000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = ""


def check_api_health():
    """Check if the Flask API is running."""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_conversation():
    """Start a new conversation session."""
    try:
        response = requests.post(
            f"{API_URL}/api/start_session",
            json={'session_id': st.session_state.session_id},
            timeout=5
        )
        if response.status_code == 200:
            st.session_state.conversation_active = True
            st.session_state.messages = []
            st.session_state.customer_id = ""
            # Add welcome message
            welcome_msg = "Hello! Welcome to Airline & Hotel Booking Support Agent. To get started, please provide your Customer ID."
            st.session_state.messages.append({
                'role': 'assistant',
                'content': welcome_msg,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            return True
        return False
    except Exception as e:
        st.error(f"Failed to start conversation: {str(e)}")
        return False


def end_conversation():
    """End the current conversation session."""
    try:
        response = requests.post(
            f"{API_URL}/api/end_session",
            json={'session_id': st.session_state.session_id},
            timeout=5
        )
        st.session_state.conversation_active = False
        st.session_state.messages = []
        st.session_state.customer_id = ""
        st.session_state.session_id = str(uuid.uuid4())
        return True
    except Exception as e:
        st.error(f"Failed to end conversation: {str(e)}")
        return False


def send_message(user_message):
    """Send a message to the agent API."""
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                'message': user_message,
                'session_id': st.session_state.session_id
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return data['response'], data.get('customer_id', '')
        return None, None
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None, None


# Sidebar
with st.sidebar:
    st.title("✈️ Control Panel")
    st.markdown("---")

    # API Status
    api_status = check_api_health()
    status_color = "🟢" if api_status else "🔴"
    status_text = "Connected" if api_status else "Disconnected"
    st.markdown(f"**API Status:** {status_color} {status_text}")

    if not api_status:
        st.warning("⚠️ API is not running. Please start the Flask server first.")
        st.code("python flask_app.py", language="bash")

    st.markdown("---")

    # Conversation Controls
    st.subheader("Conversation Controls")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Start", use_container_width=True, disabled=not api_status or st.session_state.conversation_active):
            if start_conversation():
                st.success("Conversation started!")
                st.rerun()

    with col2:
        if st.button("🛑 End", use_container_width=True, disabled=not st.session_state.conversation_active):
            if end_conversation():
                st.success("Conversation ended!")
                st.rerun()

    st.markdown("---")

    # Session Information
    st.subheader("Session Info")
    st.text(f"Session ID:\n{st.session_state.session_id[:8]}...")
    if st.session_state.customer_id:
        st.text(f"Customer ID:\n{st.session_state.customer_id}")

    st.markdown("---")

    # Help Section
    st.subheader("ℹ️ Help")
    st.markdown("""
    **I can help you with:**
    - ✈️ Flight bookings and details
    - 🏨 Hotel bookings and details
    - 👤 Customer support inquiries

    **How to use:**
    1. Click 'Start' to begin
    2. Provide your Customer ID
    3. Ask your questions
    4. Click 'End' when done
    """)


# Main Content Area
st.title("Airline & Hotel Booking Assistant")
st.markdown("Your intelligent assistant for flight and hotel bookings")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role_class = "user-message" if message['role'] == 'user' else "assistant-message"
        role_label = "You" if message['role'] == 'user' else "Assistant"

        st.markdown(f"""
            <div class="chat-message {role_class}">
                <div class="message-header">{role_label} • {message['timestamp']}</div>
                <div class="message-content">{message['content']}</div>
            </div>
        """, unsafe_allow_html=True)

# Chat input
if st.session_state.conversation_active:
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })

        # Get agent response
        with st.spinner("Agent is thinking..."):
            agent_response, customer_id = send_message(user_input)

            if agent_response:
                # Update customer ID if provided
                if customer_id:
                    st.session_state.customer_id = customer_id

                # Add agent response to chat
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': agent_response,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
            else:
                # Show error message if no response
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': 'Sorry, I encountered an error. Please try again.',
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })

        # Rerun after both messages are added
        st.rerun()
else:
    st.info("👈 Click 'Start' in the sidebar to begin a conversation")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Powered by LangGraph & Streamlit | Airline & Hotel Booking Agent"
    "</div>",
    unsafe_allow_html=True
)