import json
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState
from schemas.FiltersFormat import FiltersFormat

def helper(state: AgentState, config: RunnableConfig) -> dict:
    """Wyjaśnia użytkownikowi działanie programu oraz dostępne filtry."""
    print("--- NODE: HELPER ---")

    agent = config["configurable"]["agent"]

    filters_schema = json.dumps(FiltersFormat.model_json_schema(), indent=2, ensure_ascii=False)

    system_prompt = SystemMessage(
        content=(
            "Jesteś asystentem AI wyspecjalizowanym w wyszukiwaniu nieruchomości.\n\n"
            "Twój cel:\n"
            "Wyjaśnij użytkownikowi, jak działa aplikacja, w czym możesz mu pomóc "
            "oraz jakie kryteria/filtry wyszukiwania potrafisz rozpoznawać i przetwarzać.\n\n"
            "Jeśli użytkownik nic nie napisał to podaj informację jak możesz pomóc\n\n"
            "Oto przykład pytania które może zadać użytkownik:\n"
            "Szukam mieszkania w Warszawie na parterze z 3 pokojami.\n\n"
            "Oto techniczna struktura filtrów, które obsługuje system (przedstaw je użytkownikowi w przystępnej, czytelnej formie płynnego tekstu lub punktów, a nie surowego kodu JSON):\n"
            f"```json\n{filters_schema}\n```"
        )
    )

    full_messages = [system_prompt] + state["messages"]
    response = agent.invoke(full_messages)

    return {"messages": [response]}
