from .nodes import (SupportState,
                     intent_detect, 
                     route_to_agent, 
                     route_flight_agent_output, 
                     route_hotel_agent_output,
                     set_variables,
                     disambiguation,
                     flightAgent, 
                     hotelAgent)
from langgraph.graph import StateGraph, END




def create_support_graph():
    """Create the customer support workflow graph."""
    workflow = StateGraph(SupportState)
    flight_agent = flightAgent()
    hotel_agent= hotelAgent()
    # Add nodes
    workflow.add_node("detect_intent", intent_detect)
    workflow.add_node("disambiguation", disambiguation)


    workflow.add_node("hotel_agent", hotel_agent.hotel_agent_orchestrator)
    workflow.add_node("hotel_details", hotel_agent.hotel_details)
    workflow.add_node("all_hotels", hotel_agent.all_hotels)
    workflow.add_node("book_hotel", hotel_agent.book_hotel)
    workflow.add_node("lookup_customer_hotel", hotel_agent.lookup_customer)
    workflow.add_node("flight_agent", flight_agent.flight_agent_orchestraor)
    workflow.add_node("lookup_customer_flight", flight_agent.lookup_customer)
    workflow.add_node("flight_details", flight_agent.flight_details)
    workflow.add_node("all_flights", flight_agent.all_flights)
    workflow.add_node("book_flight", flight_agent.book_flight)
    workflow.add_node('respond_flight', flight_agent.respond)
    workflow.add_node('respond_hotel', hotel_agent.respond)
    workflow.add_node("set_variables", set_variables)

    workflow.set_entry_point("detect_intent")

    workflow.add_conditional_edges(
            "detect_intent",
            route_to_agent,
            {
                "disambiguation": "disambiguation",
                "flight_agent": "flight_agent",
                "hotel_agent": "hotel_agent",
                "set_variables": "set_variables",
                END: END # If the intent is not flight or hotel, end the workflow

            })

    workflow.add_conditional_edges(
        "flight_agent",
        route_flight_agent_output,
        {
            "lookup_customer_flight": "lookup_customer_flight",
            "flight_details": "flight_details",
            "all_flights": "all_flights",
            "book_flight": "book_flight",
            END: END, # If no specific action, just end for now
        }
    )

    workflow.add_conditional_edges(
        "hotel_agent",
        route_hotel_agent_output,
        {
            "lookup_customer_hotel": "lookup_customer_hotel",
            "hotel_details": "hotel_details",
            "all_hotels": "all_hotels",
            "book_hotel": "book_hotel",
            END: END, # If no specific action, just end for now
        }
    )
    

    # All tool nodes should lead to END once their action is completed
    workflow.add_edge("set_variables", END)
    workflow.add_edge("disambiguation", END)
    workflow.add_edge("lookup_customer_flight", 'respond_flight')
    workflow.add_edge("flight_details", 'respond_flight')
    workflow.add_edge("all_flights", 'respond_flight')
    workflow.add_edge("lookup_customer_hotel", 'respond_hotel')
    workflow.add_edge("hotel_details", 'respond_hotel')
    workflow.add_edge("all_hotels", 'respond_hotel')
    workflow.add_edge("book_flight", 'respond_flight')
    workflow.add_edge("book_hotel", 'respond_hotel')

    
    workflow.add_edge("respond_flight", END)
    workflow.add_edge("respond_hotel", END)

    return workflow.compile()
