
from langchain_core.messages import HumanMessage
from utils.state import create_support_graph

app = create_support_graph()

# Save the graph visualization
try:
    graph_png = app.get_graph().draw_mermaid_png()
    with open("workflow_graph.png", "wb") as f:
        f.write(graph_png)
    print("Graph saved to workflow_graph.png\n")
except Exception as e:
    print(f"Could not save graph: {e}\n")

# Initialize state
state = {
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

# Greeting
print("=" * 60)
print("Welcome to Airline & Hotel Booking Support Agent!")
print("=" * 60)
print("\nI can help you with:")
print("  - Flight bookings and details")
print("  - Hotel bookings and details")
print("  - Customer support inquiries")
print("\nType 'quit' or 'end' to exit the chat.\n")
print("-" * 60)

# Ask for customer ID first
print("\nAgent: Hello! To get started, please provide your Customer ID.")
customer_id_input = input("You: ").strip()

if customer_id_input.lower() in ['quit', 'end']:
    print("\nAgent: Thank you for using our service. Goodbye!")
    exit()

# Set customer ID
state["messages"].append(HumanMessage(content=customer_id_input))
result = app.invoke(state)
state = result

print(f"\nAgent: Customer ID set successfully! How can I assist you today?")
print("-" * 60)

# Main conversation loop
while True:
    user_input = input("\nYou: ").strip()

    if not user_input:
        print("Agent: Please enter a message.")
        continue

    if user_input.lower() in ['quit', 'end']:
        print("\nAgent: Thank you for using our service. Goodbye!")
        break

    # Add user message to state
    state["messages"].append(HumanMessage(content=user_input))
    state["intent"] = ""
    state["next"] = ""

    # Invoke the agent
    try:
        result = app.invoke(state)
        state = result

        # Get the last AI message
        last_message = state["messages"][-1]
        if hasattr(last_message, 'content'):
            response = last_message.content
            print(f"\nAgent : {response}")
        else:
            print(f"\nAgent: {last_message}")

        print("-" * 60)

    except Exception as e:
        print(f"\nAgent: I encountered an error: {e}")
        print("Please try again or type 'quit' to exit.")
        print("-" * 60)