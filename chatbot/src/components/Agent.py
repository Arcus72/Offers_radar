import os
from langchain_google_genai import ChatGoogleGenerativeAI


class Agent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0,
        )
        self.structured_llms = {}

    def invoke_structured(self, prompt: str, ResponseStructure):
        structure_name = ResponseStructure.__name__

        if structure_name not in self.structured_llms:
            self.structured_llms[structure_name] = self.llm.with_structured_output(ResponseStructure)

        return self.structured_llms[structure_name].invoke(prompt)

    def invoke(self, messages: str):
        return self.llm.invoke(messages)
