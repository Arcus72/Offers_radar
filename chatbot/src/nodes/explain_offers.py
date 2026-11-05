from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState

def explain_offers(state: AgentState, config: RunnableConfig) -> dict:
    """Generuje czytelne podsumowanie i opis znalezionych ofert mieszkań dla użytkownika."""
    print("--- NODE: EXPLAIN_OFFERS ---")

    agent = config["configurable"]["agent"]

    offers = state.get("collected_offers") or []
    filters = state.get("search_filters") or {}

    if not offers:
        sys_prompt = SystemMessage(
            content=(
                "Jesteś pomocnym doradcą ds. nieruchomości.\n"
                "Poinformuj użytkownika, że nie znaleziono żadnych ofert spełniających podane kryteria.\n"
                f"Aktualne kryteria wyszukiwania: {filters}.\n"
                "Uprzejmie zasugeruj poluzowanie wymagań (np. zwiększenie budżetu, zmianę lokalizacji lub zmniejszenie liczby pokoi)."
            )
        )
    else:
        sys_prompt = SystemMessage(
            content=(
                "Jesteś profesjonalnym doradcą ds. nieruchomości.\n"
                "Twoim zadaniem jest zaprezentowanie użytkownikowi znalezionych ofert mieszkań w przystępnej, atrakcyjnej i przejrzystej formie.\n\n"
                "Zasady formatowania odpowiedzi:\n"
                "1. Przedstaw najważniejsze atuty każdego mieszkania (cena, lokalizacja, metraż, liczba pokoi, piętro).\n"
                "2. Wskaż, jak oferty odnoszą się do preferencji podanych przez użytkownika.\n"
                "3. Zachowaj strukturę wypunktowaną (np. podział na konkretne oferty), używając pogrubień dla kluczowych danych.\n"
                "4. Na końcu zachęć użytkownika do dopytania o szczegóły danej oferty lub zgłoszenia chęci modyfikacji kryteriów.\n\n"
                f"Pobrane oferty do zaprezentowania:\n{offers}"
            )
        )

    full_messages = [sys_prompt] + state["messages"]

    response = agent.invoke(full_messages)

    return {"messages": response}
