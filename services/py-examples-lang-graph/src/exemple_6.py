from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


WINDOW_SECONDS = 60


class GraphState(TypedDict):
    user_id: str
    messages: list[str]
    combined_text: str


@dataclass
class MessageEvent:
    user_id: str
    message: str
    timestamp: datetime


def normalize_messages(state: GraphState) -> GraphState:
    normalized_messages = [message.strip() for message in state["messages"] if message.strip()]

    return {
        "user_id": state["user_id"],
        "messages": normalized_messages,
        "combined_text": "",
    }


def combine_messages(state: GraphState) -> GraphState:
    combined_text = "\n".join(state["messages"])

    return {
        "user_id": state["user_id"],
        "messages": state["messages"],
        "combined_text": combined_text,
    }


builder = StateGraph(GraphState)
builder.add_node("normalize_messages", normalize_messages)
builder.add_node("combine_messages", combine_messages)
builder.add_edge(START, "normalize_messages")
builder.add_edge("normalize_messages", "combine_messages")
builder.add_edge("combine_messages", END)
compiled_graph = builder.compile()


def process_user_batch(user_id: str, messages: list[str]) -> None:
    payload: GraphState = {
        "user_id": user_id,
        "messages": messages,
        "combined_text": "",
    }

    print(f"\nJanela de 60s fechada para user_id={user_id}")
    print("Payload enviado ao grafo:", payload)

    result = compiled_graph.invoke(payload)

    print("Texto consolidado final:")
    print(result["combined_text"] or "<nenhuma mensagem valida>")
    print("-" * 60)


def flush_expired_batches(
    pending_batches: dict[str, dict[str, object]],
    current_timestamp: datetime,
) -> None:
    expired_user_ids: list[str] = []

    for user_id, batch in pending_batches.items():
        last_timestamp = batch["last_timestamp"]
        assert isinstance(last_timestamp, datetime)

        if current_timestamp - last_timestamp >= timedelta(seconds=WINDOW_SECONDS):
            messages = batch["messages"]
            assert isinstance(messages, list)
            process_user_batch(user_id, list(messages))
            expired_user_ids.append(user_id)

    for user_id in expired_user_ids:
        del pending_batches[user_id]


def simulate_message_aggregation(events: list[MessageEvent]) -> None:
    pending_batches: dict[str, dict[str, object]] = {}

    for event in sorted(events, key=lambda item: item.timestamp):
        flush_expired_batches(pending_batches, event.timestamp)

        print(
            f"Mensagem recebida em {event.timestamp.strftime('%H:%M:%S')} "
            f"de user_id={event.user_id}: {event.message!r}"
        )

        if event.user_id not in pending_batches:
            pending_batches[event.user_id] = {
                "messages": [],
                "last_timestamp": event.timestamp,
            }

        batch = pending_batches[event.user_id]
        messages = batch["messages"]
        assert isinstance(messages, list)
        messages.append(event.message)
        batch["last_timestamp"] = event.timestamp

    if pending_batches:
        final_timestamp = max(
            batch["last_timestamp"] for batch in pending_batches.values()
            if isinstance(batch["last_timestamp"], datetime)
        ) + timedelta(seconds=WINDOW_SECONDS)
        flush_expired_batches(pending_batches, final_timestamp)


if __name__ == "__main__":
    base_time = datetime(2026, 4, 11, 10, 0, 0)

    events = [
        MessageEvent("user-1", "Oi", base_time),
        MessageEvent("user-1", "quero saber o status do pedido", base_time + timedelta(seconds=20)),
        MessageEvent("user-2", "   ", base_time + timedelta(seconds=30)),
        MessageEvent("user-2", "Preciso da segunda via do boleto", base_time + timedelta(seconds=40)),
        MessageEvent("user-1", "agora tambem quero alterar o endereco", base_time + timedelta(seconds=130)),
        MessageEvent("user-2", "pode mandar por email?", base_time + timedelta(seconds=150)),
    ]

    simulate_message_aggregation(events)
