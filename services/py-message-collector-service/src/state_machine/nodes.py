from __future__ import annotations

from typing import Callable

from .services import (
    GraphDependencies,
    build_client_id,
    build_response,
    consolidate_messages,
    decide_action,
    load_long_term_memory,
    save_and_load_short_term_memory,
    search_products,
)
from .state import ConversationState


def make_receive_messages_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        messages = state.get("messages", [])
        consolidated_message = consolidate_messages(messages)
        return {
            "client_id": build_client_id(state["platform"], state["user_id"]),
            "messages": messages,
            "consolidated_message": consolidated_message,
            "product_results": [],
        }

    return node


def make_load_short_term_memory_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        short_term_memory = save_and_load_short_term_memory(
            dependencies=dependencies,
            platform=state["platform"],
            user_id=state["user_id"],
            messages=state.get("messages", []),
            consolidated_message=state.get("consolidated_message", ""),
        )
        return {"short_term_memory": short_term_memory}

    return node


def make_load_long_term_memory_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        long_term_memory = load_long_term_memory(
            dependencies=dependencies,
            client_id=state["client_id"],
            short_term_memory=state.get("short_term_memory", []),
            batch_size=len(state.get("messages", [])),
        )
        return {"long_term_memory": long_term_memory}

    return node


def make_decide_action_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        action = decide_action(state.get("consolidated_message", ""))
        return {"action": action}

    return node


def make_respond_direct_node() -> Callable[[ConversationState], ConversationState]:
    def node(_: ConversationState) -> ConversationState:
        return {}

    return node


def make_search_products_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        product_results = search_products(
            dependencies=dependencies,
            query=state.get("consolidated_message", ""),
        )
        return {"product_results": product_results}

    return node


def make_build_response_node(
    dependencies: GraphDependencies,
) -> Callable[[ConversationState], ConversationState]:
    def node(state: ConversationState) -> ConversationState:
        final_response = build_response(
            dependencies=dependencies,
            platform=state["platform"],
            user_id=state["user_id"],
            consolidated_message=state.get("consolidated_message", ""),
            short_term_memory=state.get("short_term_memory", []),
            long_term_memory=state.get("long_term_memory", {}),
            product_results=state.get("product_results", []),
        )
        return {"final_response": final_response}

    return node
