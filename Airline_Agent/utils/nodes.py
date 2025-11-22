import json
import re # Import re for regular expressions
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import ToolMessage
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path to access Data folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Data.customer_data import CUSTOMER_DATA

# Load environment variables from .env file
load_dotenv()

groq_api_key = os.getenv("GROQ_KEY")
groq_model = os.getenv("GROQ_MODEL")
print("Using Groq Model:", groq_model)
print("Using Groq API Key:", groq_api_key)
from langchain_groq import ChatGroq
from .tools import get_flight_details, get_customer_details, get_all_flights, get_hotel_details, get_all_hotels
from Data.database import add_flight_to_customer, add_hotel_to_customer

# Create LLM class
llm = ChatGroq(
    model=groq_model,
    temperature=0.7,
    max_retries=2,
    api_key=groq_api_key,
)

import sqlite3
import time
class IntentSchema(TypedDict):
    intent: str
class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], "Conversation messages"]
    human_message: Annotated[List[BaseMessage], "Latest message from the user"]
    customer_id: Annotated[str, "Customer ID"]
    ticket_id: Annotated[str, "Support ticket ID"]
    hotel_id: Annotated[str, "Hotel ID"]
    tools: Annotated[List, "Available tools"]
    issue_type: Annotated[str, "Type of issue"]
    intent: Annotated[str, "Intent of the customer"]
    resolution_status: Annotated[str, "Current resolution status"]
    next: Annotated[str, "Next action"]
def intent_detect(state: SupportState) -> SupportState:
    """Detect Intent of user."""
    messages = state["messages"]
    last_message = messages[-1]
    state['human_message']= last_message.content
    system_prompt = """
    You are a intent detection agent. Your task is identify the intent of the user and pick one of the intent strictly:
    customer_support_help: need help with ticket or issues
    set_state_variables: if user inputs customer-id, set the state variables
    book_flight: need to book a flight
    my_flight_details: need to get my flight details
    my_hotel_details: need to get my hotel details
    all_hotel_details: need hotel details as per location asked
    all_flight_details: need flight details as per departure airport asked
    book_hotel: need to book a hotel
    disambiguation: if the user's request is ambiguous and does not fit the above actions
    Strictly return just the intent without any explanation in a JSON format. Example:
    {"intent": "customer_support_help"}
    """

    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    response_content = response.content.strip()

    # Extract JSON string from markdown code block
    match = re.search(r'```json\n(.*?)```', response_content, re.DOTALL)
    if match:
        json_string = match.group(1).strip()
    else:
        json_string = response_content # Fallback if no markdown block is found

    # Parse the JSON string to extract the intent
    try:
        intent_data = json.loads(json_string)
        intent = intent_data.get("intent")
    except json.JSONDecodeError:
        # Handle cases where the LLM might not return perfect JSON
        intent = "unknown" # or some default handling
    print("Detected intent:", intent)
    return {
        **state,
        "messages": messages + [response],
        "intent": intent
    }

def route_to_agent(state: SupportState) -> str:
    """Route to the appropriate specialized agent."""
    intent = state.get("intent", "general_travel")

    routing_map = {
        "set_state_variables": 'set_variables', 
        "book_flight": "flight_agent",
        "my_flight_details": "flight_agent",
        "all_flight_details": "flight_agent",
        "my_hotel_details": "hotel_agent",
        "all_hotel_details": "hotel_agent",
        "book_hotel": "hotel_agent",
        "disambiguation": "disambiguation",
        "customer_support_help": END, # Route to END for now if no specific agent
    }

    return routing_map.get(intent, END) # Default to END if intent is unknown
def set_variables(state: SupportState) -> SupportState:
    """Set necessary variables based on intent."""
    messages= state["messages"]
    last_message= messages[-2].content
    system_prompt= f"""
    Extract the customer ID from the last message. Only display the customer ID.
    Do not explain. last message: {last_message}"""
    state['human_message']= last_message
    response= llm.invoke([HumanMessage(content=system_prompt)])
    customer_id= response.content.strip()
    for c in CUSTOMER_DATA:
        if c["customer_id"].lower() in customer_id.lower():
            state["customer_id"]= c["customer_id"]
            state["ticket_id"]= c["FLIGHT_ID"]
            state["hotel_id"]= c["HOTEL_ID"]
            print("Set state variables:", state["customer_id"], state["ticket_id"], state["hotel_id"])
            break
    state["messages"]= messages + [AIMessage(content=f"Set customer ID to {state['customer_id']}. How can I assist you further?")]
    return state
def route_flight_agent_output(state: SupportState) -> str:
    """Route from flight agent based on 'next' field."""
    next_action = state.get("next")
    if next_action == "lookup_customer":
        return "lookup_customer_flight"
    elif next_action == "flight_details":
        return "flight_details"
    elif next_action == "all_flights":
        return "all_flights"
    elif next_action == "book_flight":
        return "book_flight"
    else:
        return END # If no specific action, just end for now

def route_hotel_agent_output(state: SupportState) -> str:
    """Route from hotel agent based on 'next' field."""
    next_action = state.get("next")
    if next_action == "lookup_customer":
        return "lookup_customer_hotel"
    elif next_action == "hotel_details":
        return "hotel_details"
    elif next_action == "all_hotels":
        return "all_hotels"
    elif next_action == "book_hotel":
        return "book_hotel"
    else:
        return END # If no specific action, just end for now


def disambiguation(state: SupportState) -> SupportState:
      """Handle disambiguation when user request is unclear."""
      messages = state["messages"]
      user_message = state.get('human_message', messages[-1].content if messages else '')
      system_prompt = f"""
      The user's request is ambiguous. The question must be regarding travel bookings (flight and hotels) or details.
      Ask a clarifying question to better understand their needs. 
      If it's not related to travel bookings, politely inform them that you can only assist with travel-related queries.

      User's message: {user_message}
      """

      response = llm.invoke([HumanMessage(content=system_prompt)])

      return {
          **state,
          "messages": messages + [response],
          "next": "end"
      }


class flightAgent:
  def __init__(self) -> None:
      self.llm=llm
      self.tools = [get_flight_details, get_customer_details, get_all_flights]
  def flight_agent_orchestraor(self,state: SupportState) -> SupportState:
    messages = state["messages"]
    tools = state["tools"]
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])

    flight_tools=[tool for tool in tools if tool.name in ["get_flight_details", "get_all_flights", "get_customer_details"]]
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in flight_tools])
    system_prompt = f"""
    You are a Flight Booking Agent. Analyze the user's message and determine the best action.

    Available tools:
    {tool_descriptions}

    Current conversation:
    {messages}

    Determine the next action based on the user's message:
    - "flight_details" if they need their flight details
    - "all_flights" if they want to see all flights
    - "lookup_customer" if they need their customer details
    - "book_flight" if they want to book a specific flight
    


    Respond with just the action name.
    """

    response = llm.invoke([HumanMessage(content=system_prompt)])

    # Determine next action based on response
    action = response.content.strip().lower()

    return {**state, "next": action}
  
  def lookup_customer(self, state: SupportState) -> SupportState:
      """Look up customer information."""
      customer_id = state["customer_id"]
      result = get_customer_details.invoke({"customer_id": customer_id})

      tool_message = ToolMessage(content=result, tool_call_id="lookup_customer")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }
  def flight_details(self,state: SupportState) -> SupportState:
      """Get flight details."""


      flight_id = state["ticket_id"]
      result = get_flight_details.invoke({"flight_id": flight_id}) # Corrected tool call

      tool_message = ToolMessage(content=result, tool_call_id="flight_details")

      return {
          **state,
          "messages": state["messages"] + [tool_message] ,
          "next": "respond"
      }
  def all_flights(self,state: SupportState) -> SupportState:
      """Get all flights."""
      last_message = state["human_message"]
      print('last message', last_message)
      system_prompt = f"""
      Extract the departure airport from the last message: {last_message}. Only display the departure airport. Do not explain.
      MUST MAP TO ONE OF THE FOLLOWING AIRPORTS:
      JFK, LAX, ORD, SFO
      Departure Airport:
      """
      response = llm.invoke([HumanMessage(content=system_prompt)])
      departure_airport = response.content.strip().upper()
      result = get_all_flights.invoke({"departure_airport": departure_airport}) # Corrected tool call

      tool_message = ToolMessage(content=result, tool_call_id="all_flights")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def book_flight(self, state: SupportState) -> SupportState:
      """Book a flight by updating the database."""
      last_message = state["human_message"]
      customer_id = state.get("customer_id")

      # Extract flight_id from the message
      system_prompt = f"""
      Extract the flight ID from the message: {last_message}, OR if not explicitly mentioned,
      infer the most suitable flight ID based on the past conversations and tool data {state['messages']}.
      Only display the flight ID (e.g., FLIGHT123). Do not explain.
      Flight ID:
      """
      response = llm.invoke([HumanMessage(content=system_prompt)])
      print('response in book flight', response.content)
      flight_id = response.content.strip().upper()

      # Update database
      success = add_flight_to_customer(customer_id, flight_id)

      if success:
          result = f"Successfully booked flight {flight_id} for customer {customer_id}"
          state["ticket_id"] = flight_id  # Update state with new flight_id
          print(result)
      else:
          result = f"Failed to book flight {flight_id}. Customer {customer_id} may not exist in the database."
          print(result)

      tool_message = ToolMessage(content=result, tool_call_id="book_flight")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def respond(self, state: SupportState) -> SupportState:
      """Generate a response to the user."""
      messages = state["messages"]
      laast_message_content = messages[-1].content
      print('messages in respond', messages[-1])
      system_prompt = f"""
      You are a helpful flight booking assistant. 
      Use the information from the tools to respond to the user's query.
      user Query: {state['human_message']}
      message from the tool: {laast_message_content}
      """

      response = llm.invoke([HumanMessage(content=system_prompt)])

      print('response in flight respond', response)

      return {
          **state,
          "messages": messages + [response],
          "next": "end"
      }

class hotelAgent:
  def __init__(self) -> None:
      self.llm=llm
      self.tools = [get_hotel_details, get_customer_details, get_all_hotels]

  def hotel_agent_orchestrator(self,state: SupportState) -> SupportState:
    messages = state["messages"]
    tools = state["tools"]

    hotel_tools=[tool for tool in tools if tool.name in ["get_hotel_details", "get_all_hotels", "get_customer_details"]]
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in hotel_tools])
    system_prompt = f"""
    You are a Hotel Booking Agent. Analyze the user's message and determine the best action.

    Available tools:
    {tool_descriptions}

    Current conversation:
    {messages}

    Determine the next action based on the user's message:
    - "hotel_details" if they need their hotel details
    - "all_hotels" if they want to see all hotels
    - "lookup_customer" if they need their customer details
    - "book_hotel" if they want to book a specific hotel


    Respond with just the action name.
    """

    response = llm.invoke([HumanMessage(content=system_prompt)])

    # Determine next action based on response
    action = response.content.strip().lower()
    print("Determined hotel agent action:", action)

    return {**state, "next": action}

  def lookup_customer(self, state: SupportState) -> SupportState:
      """Look up customer information."""
      customer_id = state["customer_id"]
      result = get_customer_details.invoke({"customer_id": customer_id})

      tool_message = ToolMessage(content=result, tool_call_id="lookup_customer")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def hotel_details(self,state: SupportState) -> SupportState:
      """Get hotel details."""
      hotel_id = state["hotel_id"]
      result = get_hotel_details.invoke({"hotel_id": hotel_id})

      tool_message = ToolMessage(content=result, tool_call_id="hotel_details")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def all_hotels(self,state: SupportState) -> SupportState:
      """Get all hotels."""
      last_message = state["human_message"]
      print('last message', last_message)
      system_prompt = f"""
      Identify the location from the message: {last_message}.
      MUST MAP TO ONE OF THE FOLLOWING LOCATIONS (exact match):
      - New York
      - Chicago
      - San Fransisco

      Return ONLY the location name, nothing else.
      Location:
      """
      response = llm.invoke([HumanMessage(content=system_prompt)])
      location = response.content.strip()
      print('extracted location:', location)
      result = get_all_hotels.invoke({"location": location})

      tool_message = ToolMessage(content=result, tool_call_id="all_hotels")
      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def book_hotel(self, state: SupportState) -> SupportState:
      """Book a hotel by updating the database."""
      last_message = state["human_message"]
      customer_id = state.get("customer_id")

      # Extract hotel_id from the message or conversation history
      system_prompt = f"""
      Extract the hotel ID from the user's message OR from the conversation history.

      User's message: {last_message}

      Recent conversation: {state['messages'][-3:] if len(state['messages']) >= 3 else state['messages']}

      Look for a hotel ID in the format HOTELXXX (e.g., HOTEL123, HOTEL456).
      If the user mentioned a hotel name or asked about hotels, find the corresponding hotel ID from the conversation.

      Return ONLY the hotel ID in the format HOTELXXX. Do not explain.
      Hotel ID:
      """
      response = llm.invoke([HumanMessage(content=system_prompt)])
      hotel_id = response.content.strip().upper()
      print(f"Extracted hotel_id: {hotel_id}")

      # Validate hotel_id format
      if not hotel_id.startswith("HOTEL") or hotel_id == "NONE" or hotel_id == "HOTELXXX":
          result = f"Could not identify a valid hotel ID. Please specify which hotel you'd like to book (e.g., HOTEL123, HOTEL456)."
          print(result)
      else:
          # Update database
          success = add_hotel_to_customer(customer_id, hotel_id)

          if success:
              result = f"Successfully booked hotel {hotel_id} for customer {customer_id}"
              state["hotel_id"] = hotel_id  # Update state with new hotel_id
              print(result)
          else:
              result = f"Failed to book hotel {hotel_id}. Customer {customer_id} may not exist in the database."
              print(result)

      tool_message = ToolMessage(content=result, tool_call_id="book_hotel")

      return {
          **state,
          "messages": state["messages"] + [tool_message],
          "next": "respond"
      }

  def respond(self, state: SupportState) -> SupportState:
      """Generate a response to the user."""
      messages = state["messages"]
      print('messages in respond', messages[-1])
      last_message = messages[-1]
      system_prompt = f"""
      You are a helpful hotel booking assistant.
      Use the message from the tools to create a user-friendly response. Also, display the hotel id.
      Human Query: {state['human_message']} 
      message from the tool: {last_message}
      """

      response = llm.invoke([HumanMessage(content=system_prompt)])
      print('response in hotel respond', response)

      return {
          **state,
          "messages": messages + [response],
          "next": "end"
      }