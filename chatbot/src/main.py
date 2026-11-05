import json
import sys
from httpx import ConnectError
from components.Agent import Agent
from graph import build_graph
from state import AgentState

agent = Agent()
app = build_graph()

print("=" * 60)
print("  Witaj w Asystencie Nieruchomości!")
print("  Pomogę Ci znaleźć idealne mieszkanie na podstawie Twoich wymagań.")
print("  Wpisz 'wyjście' lub 'exit', aby zakończyć rozmowę.")
print("=" * 60)

conversation_state: AgentState = {
    "messages": [],
    "search_filters": {},
    "missing_keys": [],
    "collected_offers": []
}

while True:
    try:
        user_input = input("\nUżytkownik > ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nDo zobaczenia!")
        break

    if not user_input:
        continue

    if user_input.lower() in ["wyjście", "exit", "quit"]:
        print("\nDziękuję za skorzystanie z asystenta. Do zobaczenia!")
        break

    conversation_state["messages"].append(("user", user_input))

    # --- Catch errors from llm and db connection ---
    try:
        conversation_state = app.invoke(
            conversation_state,
            config={"configurable": {"agent": agent}}
        )
    except (ConnectError, ConnectionError, TimeoutError) as e:
        conversation_state["messages"].pop()

        print("\n" + "=" * 40)
        print(f"[BŁĄD KRYTYCZNY] Wyczerpano limity ponowień (RetryPolicy). Brak połączenia z API LLM.")
        print(f"Szczegóły: {e}")
        print("Aplikacja zostanie zamknięta.")
        print("=" * 40)
        sys.exit(1)

    except Exception as e:
        conversation_state["messages"].pop()

        print("\n" + "=" * 40)
        print(f"[BŁĄD KRYTYCZNY] Wystąpił nieoczekiwany błąd podczas wykonywania grafu: {e}")
        print("Aplikacja zostanie zamknięta.")
        print("=" * 40)
        sys.exit(1)

    # --- Display message ---
    last_message = conversation_state["messages"][-1]
    content = getattr(last_message, "content", last_message)

    #### Display search_filters and collected_offers
    # print("\n\n")
    # print(json.dumps(conversation_state["search_filters"], indent=2, ensure_ascii=False))
    # print("\n\n")
    # print(json.dumps(conversation_state["collected_offers"], indent=2, ensure_ascii=False, default=str))


    print("\n" + "-" * 40)
    print("Agent:")
    if isinstance(content, list):
        text_content = "\n".join(
            block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text"
        )
        print(text_content)
    else:
        print(content)
    print("-" * 40)



#### FOR GRAPH TO PNG
# png_bytes = app.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

# print("Graph rendered and saved as graph.png")
