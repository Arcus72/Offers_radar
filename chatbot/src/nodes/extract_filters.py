from state import AgentState
from schemas.FiltersFormat import FiltersFormat
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from utils.is_non_empty import is_non_empty


def extract_filters(state: AgentState, config: RunnableConfig) -> dict:
    """Wyciąga filtry wyszukiwania z historii rozmowy i zapisuje je w stanie agenta."""
    print("--- NODE: EXTRACT FILTERS ---")

    agent = config["configurable"]["agent"]

    sys_prompt = SystemMessage(content=(
        "Przeanalizuj rozmowę i wyciągnij kryteria wyszukiwania nieruchomości do schematu.\n"
        "- Dla konkretnych liczb używaj `exact_value` (parter/piętro 0 = 0).\n"
        "- Zakresy (`min_value`/`max_value`) stosuj tylko przy słowach typu 'od', 'do', 'min', 'max'.\n"
    ))

    messages = [sys_prompt] + state["messages"]

    res: FiltersFormat = agent.invoke_structured(messages, FiltersFormat)

    filters = res.model_dump()
    REQUIRED_KEYS = [{"name": "city", "desc": "miasto/miasta"}]

    missing = [key for key in REQUIRED_KEYS if not is_non_empty(filters.get(key["name"]))]

    return {
        "search_filters": filters,
        "missing_keys": missing
    }
