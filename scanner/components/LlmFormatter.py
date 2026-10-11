
from typing import Generic, TypeVar
from langchain_ollama import ChatOllama
from pydantic import BaseModel
import os

T = TypeVar("T", bound=BaseModel)

SYSTEM_PROMPT = (
    "Your task is to fill up response_format based on the "
    "accommodation's description. Use only information stated in the offer; "
    "if a value is not stated, set it to null instead of guessing. "
    "Write text values in Polish, as they appear in the offer, except "
    "fields with allowed values: pick one of them."
)

class LlmFormatter(Generic[T]):
    def __init__(self, response_format: type[T]):
        llm = ChatOllama(
            model="qwen3.5:9b",
            base_url=os.environ["OLLAMA_BASE_URL"],
            reasoning=False,
            temperature=0,
            num_ctx=8192,
        )
        self.response_format = response_format
        props = response_format.model_json_schema()["properties"]
        self.system_prompt = SYSTEM_PROMPT + "\n\nFields:\n" + "\n".join(
            f"- {name}: {field.description}" + "".join(
                f" Dozwolone wartości: {', '.join(s['enum'])}."
                for s in props[name].get("anyOf", []) if "enum" in s
            )
            for name, field in response_format.model_fields.items()
        )
        self.llm = llm.with_structured_output(response_format, method="json_schema")

    def format(self, description: str) -> T:
        return self.llm.invoke([("system", self.system_prompt), ("user", description)])
