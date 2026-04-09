from __future__ import annotations

from typing import Any, Literal, TypedDict


GraphAction = Literal["respond_direct", "search_products"]


class ConversationState(TypedDict, total=False):
    platform: str
    user_id: str
    client_id: str
    messages: list[str]
    consolidated_message: str
    short_term_memory: list[dict[str, str]]
    long_term_memory: dict[str, Any]
    action: GraphAction
    product_results: list[dict[str, Any]]
    final_response: str
