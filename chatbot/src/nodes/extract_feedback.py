from state import AgentState
from schemas.FiltersFormat import FiltersFormat
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from typing import Any
import json
from utils.is_non_empty import is_non_empty

def extract_feedback(state: AgentState, config: RunnableConfig) -> dict:
    """
    Aktualizuje istniejące filtry (search_filters) na podstawie nowej wiadomości/feedbacku od użytkownika.
    Zachowuje dotychczas ustalone parametry, modyfikując lub dodając tylko te wspomniane w poprawce.
    """
    print("--- NODE: EXTRACT FEEDBACK ---")

    agent = config["configurable"]["agent"]
    current_filters = state.get("search_filters", {})

    current_filters_json = json.dumps(current_filters, ensure_ascii=False, indent=2)

    sys_prompt = SystemMessage(content=(
        "Twoim zadaniem jest AKTUALIZACJA istniejących wymagań dotyczących mieszkania na podstawie "
        "nowych uwag, poprawek lub doprecyzowań (feedbacku) podanych przez użytkownika.\n\n"
        f"OBECNIE USTALONE FILTRY:\n```json\n{current_filters_json}\n```\n\n"
        "ZASADY AKTUALIZACJI:\n"
        "1. ZACHOWAJ wszystkie dotychczasowe filtry z powższego JSON-a, jeśli użytkownik ich nie zmienił ani nie wycofał.\n"
        "2. NADPISZ lub DODAJ parametry, które użytkownik bezpośrednio zmienił lub doprecyzował w swojej ostatniej wypowiedzi.\n"
        "3. USUŃ (ustaw na null), jeśli użytkownik wyraźnie zrezygnował z jakiegoś wymagania (np. 'jednak bez balkonu', 'obojętnie które piętro').\n\n"
        "ZASADY dla pól typu RangeFormat (min_value / exact_value / max_value):\n"
        "- Użyj 'exact_value' gdy użytkownik podaje KONKRETNĄ liczbę bez słów sugerujących zakres (np. 'jednak 3 pokoje', 'zmiana na 2 piętro').\n"
        "- Użyj 'min_value' WYŁĄCZNIE gdy użyto słów: 'co najmniej', 'minimum', 'od X', 'przynajmniej', 'nie mniej niż', 'powyżej'.\n"
        "- Użyj 'max_value' WYŁĄCZNIE gdy użyto słów: 'maksymalnie', 'do X', 'nie więcej niż', 'poniżej', 'co najwyżej'.\n"
        "- Jeśli użytkownik podaje zakres (np. '2-3 pokoje'), ustaw min_value=2 i max_value=3.\n\n"
        "KRYTYCZNA ZASADA — ZERO (0) NIE JEST NULL:\n"
        "Liczba 0 (zero) jest POPRAWNĄ wartością liczbową. Gdy użytkownik mówi 'parter', 'piętro 0', 'piętrze 0' "
        "lub 'zerowe piętro', MUSISZ ustawić floor.exact_value = 0. NIE ustawiaj floor na null!\n\n"
        "PRZYKŁADY AKTUALIZACJI:\n"
        "- Stare: cena do 3000 -> Nowa wiadomość: 'Jednak wolę do 2500 zł' → price.max_value = 2500\n"
        "- Stare: Katowice -> Nowa wiadomość: 'Zmień miasto na Gliwice' → city = ['Gliwice']\n"
        "- Stare: brak piętra -> Nowa wiadomość: 'wolałbym parter' → floor.exact_value = 0\n"
        "- Stare: 2 pokoje -> Nowa wiadomość: 'jednak 3 sypialnie' → rooms.exact_value = 3\n"
    ))

    messages = [sys_prompt] + state["messages"]

    res: FiltersFormat = agent.invoke_structured(messages, FiltersFormat)

    updated_filters = res.model_dump()

    REQUIRED_KEYS = [{"name": "city", "desc": "miasto/miasta"}]
    missing = [key for key in REQUIRED_KEYS if not is_non_empty(updated_filters.get(key["name"]))]

    return {
        "search_filters": updated_filters,
        "missing_keys": missing
    }
