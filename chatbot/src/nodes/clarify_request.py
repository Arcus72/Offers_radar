from state import AgentState
from langchain_core.messages import AIMessage

def clarify_request(state: AgentState) -> dict:
    """Prosi użytkownika o podanie dodatkowych kryteriów"""
    print("NODE: clarity_request")

    missing_keys = state.get("missing_keys") or []
    response = "Aby wyszukiwanie działało poprawnie należy podać: \n"
    for key in missing_keys:
        response += f"- {key['desc']}\n"


    return {
        "messages": [AIMessage(content=response)]
    }
