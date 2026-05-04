from recommender import recommend_for_user, recommendation_reason


def format_items(title, items, empty_message):
    """Convert a list of history items into readable chatbot text."""
    if not items:
        return empty_message

    lines = [title]
    for item in items:
        product = item["product_name"]
        category = item["category"]
        query = item.get("query", "")
        duration = item.get("duration_seconds", 0)

        if query:
            lines.append(f"- {query} ({category})")
        elif duration:
            lines.append(f"- {product} ({category}) - {duration} seconds")
        else:
            lines.append(f"- {product} ({category})")

    return "\n".join(lines)


def get_history_response(user_id, user_data):
    """Show search, view, and watch history for the selected user."""
    user = user_data[user_id]

    search_text = format_items(
        "Search history:",
        user["search_history"],
        "Search history: no searches found.",
    )
    view_text = format_items(
        "View history:",
        user["view_history"],
        "View history: no viewed products found.",
    )
    watch_text = format_items(
        "Watch history:",
        user["watch_history"],
        "Watch history: no watched items found.",
    )

    return f"{search_text}\n\n{view_text}\n\n{watch_text}"


def get_wishlist_response(user_id, user_data):
    """Show wishlist items for the selected user."""
    return format_items(
        "Wishlist / saved items:",
        user_data[user_id]["wishlist"],
        "Your wishlist is empty.",
    )


def get_recommendation_response(user_id, user_data, logs_df):
    """Show recommendations with a short explanation."""
    recommendations = recommend_for_user(user_id, user_data, logs_df)
    reason = recommendation_reason(user_id, user_data)
    lines = ["Recommended for you:"]

    for product in recommendations:
        lines.append(f"- {product}")

    return f"{chr(10).join(lines)}\n\nReason: {reason}"


def respond_to_message(message, user_id, user_data, logs_df):
    """Rule-based chatbot response handler."""
    text = message.lower().strip()

    if any(word in text for word in ["recommend", "suggest", "something", "product"]):
        return get_recommendation_response(user_id, user_data, logs_df)

    if any(word in text for word in ["history", "searched", "watched", "viewed"]):
        return get_history_response(user_id, user_data)

    if any(word in text for word in ["wishlist", "saved", "save"]):
        return get_wishlist_response(user_id, user_data)

    if any(word in text for word in ["hello", "hi", "hey"]):
        return (
            "Hello. I can analyze your web activity logs and help with "
            "recommendations, history, and wishlist details."
        )

    return (
        "I can help with three things: ask 'recommend me something', "
        "'show my history', or 'show my wishlist'."
    )
