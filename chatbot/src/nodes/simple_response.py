from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState


def simple_response(state: AgentState, config: RunnableConfig) -> dict:
    """Informuje użytkownika, że jego pytanie wykracza poza zakres działania aplikacji."""
    print("--- NODE: SIMPLE_RESPONSE ---")

    agent = config["configurable"]["agent"]

    system_prompt = SystemMessage(
        content=(
            "Jesteś asystentem AI wyspecjalizowanym wyłącznie w wyszukiwaniu nieruchomości. "
            "Uprzejmie poinformuj użytkownika, że jego pytanie wykracza poza Twój zakres kompetencji. "
            "Zaproponuj pomoc w znalezieniu mieszkania lub zasugeruj wpisanie komendy 'help' w celu uzyskania instrukcji."
        )
    )

    full_messages = [system_prompt] + state["messages"]
    response = agent.invoke(full_messages)

    return {"messages": [response]}
