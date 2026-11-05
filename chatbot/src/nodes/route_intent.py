from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from state import AgentState
from schemas.RouteIntentResponse import RouteIntentResponse, RouteIntent

def route_intent(state: AgentState, config: RunnableConfig) -> RouteIntent:
    """Określa intencję użytkownika na podstawie ostatniej wiadomości oraz kontekstu stanu."""
    print("--- NODE: Route Intent ---")

    agent = config["configurable"]["agent"]
    last_message = state["messages"][-1]

    text = last_message.text if hasattr(last_message, "text") else str(last_message.content)
    clean_text = text.lower().strip()

    if clean_text in ["help", "pomoc", "?", "/help"]:
        return "helper"

    has_active_filters = bool(state.get("search_filters"))
    has_listings = bool(state.get("listings"))

    sys_prompt = SystemMessage(content=(
        "Sklasyfikuj intencję ostatniej wiadomości użytkownika.\n\n"
        f"Kontekst: Aktywne filtry: {'TAK' if has_active_filters else 'NIE'} | Pokazane oferty: {'TAK' if has_listings else 'NIE'}\n\n"
        "KLASY:\n"
        "1. 'extract_filters': Użytkownik podaje parametry szukanego mieszkania (miasto, cena, pokoje, piętro) lub rozpoczyna nowe wyszukiwanie.\n"
        "2. 'extract_feedback': Użytkownik zmienia/odrzuca pokazywane oferty lub istniejące filtry (wymaga aktywnych filtrów lub ofert).\n"
        "3. 'helper': Pytanie o zasady działania programu, dostępność filtrów lub prośba o pomoc.\n"
        "4. 'simple_response': Powitanie, podziękowanie, pogawędka lub pytanie ogólne."
    ))

    res: RouteIntentResponse = agent.invoke_structured([sys_prompt, last_message], RouteIntentResponse)

    print(f"route_intent response: {res.response}")

    return res.response
