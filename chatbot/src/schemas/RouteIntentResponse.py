from pydantic import BaseModel, Field
from typing import Literal

RouteIntent = Literal["simple_response", "extract_filters", "extract_feedback", "helper"]

class RouteIntentResponse(BaseModel):
    response: RouteIntent = Field(
        description=(
            "Intencja użytkownika: "
            "'extract_filters' gdy szuka mieszkania lub podaje kryteria, "
            "'simple_response' dla ogólnych pytań i pogawędek, "
            "'extract_feedback' gdy modyfikuje istniejące wyniki/filtry, "
            "'helper' gdy pyta o działanie programu lub pomoc."
        )
    )
