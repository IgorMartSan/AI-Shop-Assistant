from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .nodes import (
    make_build_response_node,
    make_decide_action_node,
    make_load_long_term_memory_node,
    make_load_short_term_memory_node,
    make_receive_messages_node,
    make_respond_direct_node,
    make_search_products_node,
)
from .services import GraphDependencies
from .state import ConversationState


def build_conversation_graph(dependencies: GraphDependencies):
    builder = StateGraph(ConversationState)

    builder.add_node("receive_messages", make_receive_messages_node(dependencies))
    builder.add_node(
        "load_short_term_memory",
        make_load_short_term_memory_node(dependencies),
    )
    builder.add_node(
        "load_long_term_memory",
        make_load_long_term_memory_node(dependencies),
    )
    builder.add_node("decide_action", make_decide_action_node(dependencies))
    builder.add_node("respond_direct", make_respond_direct_node())
    builder.add_node("search_products", make_search_products_node(dependencies))
    builder.add_node("build_response", make_build_response_node(dependencies))

    builder.add_edge(START, "receive_messages")
    builder.add_edge("receive_messages", "load_short_term_memory")
    builder.add_edge("load_short_term_memory", "load_long_term_memory")
    builder.add_edge("load_long_term_memory", "decide_action")
    builder.add_conditional_edges(
        "decide_action",
        lambda state: state["action"],
        {
            "respond_direct": "respond_direct",
            "search_products": "search_products",
        },
    )
    builder.add_edge("respond_direct", "build_response")
    builder.add_edge("search_products", "build_response")
    builder.add_edge("build_response", END)

    return builder.compile()
