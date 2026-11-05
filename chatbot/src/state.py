from typing import Annotated, Sequence, TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from schemas.FiltersFormat import FiltersFormat

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    search_filters: Optional[FiltersFormat]
    missing_keys: List[Dict[str, Any]]
    collected_offers: List[Dict]

