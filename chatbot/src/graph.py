from langgraph.graph import StateGraph, START, END
from state import AgentState
from httpx import ConnectError
from psycopg2 import OperationalError, DatabaseError
from langgraph.types import RetryPolicy
from nodes import (
    clarify_request,
    explain_offers,
    extract_filters,
    get_offers,
    simple_response,
    route_after_filters,
    route_intent,
    extract_feedback,
    helper
)

def build_graph():
    graph = StateGraph(AgentState)

    llm_retry_policy = RetryPolicy(
        retry_on=(ConnectError, ConnectionError, TimeoutError),
        max_attempts=3,
        initial_interval=2.0,
        backoff_factor=2.0
    )

    db_retry_policy = RetryPolicy(
        retry_on=(OperationalError, DatabaseError, ConnectionResetError),
        max_attempts=4,
        initial_interval=0.5,
        backoff_factor=1.5
    )
    graph.add_node("extract_filters", extract_filters, retry_policy=llm_retry_policy )
    graph.add_node("get_offers", get_offers, retry_policy=db_retry_policy)
    graph.add_node("explain_offers", explain_offers, retry_policy=llm_retry_policy)
    graph.add_node("clarify_request", clarify_request, retry_policy=llm_retry_policy)
    graph.add_node("simple_response", simple_response, retry_policy=llm_retry_policy)
    graph.add_node("extract_feedback", extract_feedback, retry_policy=llm_retry_policy)
    graph.add_node("helper", helper, retry_policy=llm_retry_policy)

    # Krawędzie
    graph.add_conditional_edges(START, route_intent)
    graph.add_conditional_edges("extract_filters", route_after_filters)

    graph.add_edge("extract_feedback", "get_offers")
    graph.add_edge("get_offers", "explain_offers")
    graph.add_edge("helper", END)
    graph.add_edge("clarify_request", END)
    graph.add_edge("explain_offers", END)
    graph.add_edge("simple_response", END)

    return graph.compile()
