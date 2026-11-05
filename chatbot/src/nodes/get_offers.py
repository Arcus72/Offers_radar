
from state import AgentState
from components.DatabaseManager import DatabaseManager
from schemas.FiltersFormat import FiltersFormat
import os

def get_offers(state: AgentState) -> dict:
    """Wykonuje zapytanie do bazy danych / API / bazy wektorowej"""
    print("--- NODE: GET OFFERS ---")
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    raw_filters = state.get("filters", {})

    if isinstance(raw_filters, dict):
        filters = FiltersFormat(**raw_filters)
    else:
        filters = raw_filters

    with DatabaseManager(db_name, db_user, db_pass, db_host, db_port) as db:
        offers = db.get_filtered_offers(filters )

        cleaned_offers = [
            {k: v for k, v in offer.items() if v is not None}
            for offer in offers
        ]

        return {"collected_offers": cleaned_offers}

    return state
