from typing import Literal
from state import AgentState

def route_after_filters(state: AgentState) -> Literal["get_offers", "clarify_request"]:
    """Sprawdza, czy w stanie znajdują się brakujące wymagane klucze."""

    missing_keys = state.get("missing_keys") or []

    if bool(missing_keys):
        return "clarify_request"

    return "get_offers"
