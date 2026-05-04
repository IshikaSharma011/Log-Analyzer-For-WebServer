from collections import Counter, defaultdict


def most_searched_categories(logs_df):
    """Find categories that appear most often in search logs."""
    searches = logs_df[logs_df["action"] == "search"]
    return searches["category"].value_counts()


def most_viewed_products(logs_df):
    """Find products with the highest number of page views."""
    views = logs_df[logs_df["action"] == "view"]
    return views["product_name"].value_counts()


def frequently_watched_items(logs_df):
    """Find videos or items with the highest watch time."""
    watched = logs_df[logs_df["action"] == "watch"]
    return watched.groupby("product_name")["duration_seconds"].sum().sort_values(ascending=False)


def build_category_product_map(logs_df):
    """Create a simple category to products lookup table."""
    category_products = defaultdict(Counter)

    for _, row in logs_df.iterrows():
        category = row["category"]
        product = row["product_name"]

        if category and product:
            category_products[category][product] += 1

    return category_products


def recommend_for_user(user_id, user_data, logs_df, limit=5):
    """Generate recommendations using beginner-friendly frequency logic."""
    if user_id not in user_data:
        return ["No user data found."]

    user = user_data[user_id]
    category_products = build_category_product_map(logs_df)
    user_categories = Counter()
    already_seen = set()

    for section in ["search_history", "watch_history", "wishlist", "view_history"]:
        for item in user[section]:
            user_categories[item["category"]] += 1
            already_seen.add(item["product_name"])

    recommendations = []

    for category, _ in user_categories.most_common():
        popular_items = category_products.get(category, {})
        for product, _ in popular_items.most_common():
            if product not in already_seen and product not in recommendations:
                recommendations.append(product)

    # If the selected user has already seen everything in their categories,
    # fall back to globally popular products.
    if len(recommendations) < limit:
        global_products = logs_df["product_name"].value_counts()
        for product in global_products.index:
            if product not in already_seen and product not in recommendations:
                recommendations.append(product)

    return recommendations[:limit] or ["No new recommendations available right now."]


def recommendation_reason(user_id, user_data):
    """Create a friendly explanation for why recommendations were selected."""
    user = user_data.get(user_id, {})
    searched_categories = [item["category"] for item in user.get("search_history", [])]

    if searched_categories:
        top_category = Counter(searched_categories).most_common(1)[0][0]
        return f"Users who searched for {top_category} items often explore related popular products."

    return "Recommendations are based on the most popular products in the complete log data."


def analytics_summary(logs_df):
    """Return all dashboard analytics in one dictionary."""
    return {
        "searched_categories": most_searched_categories(logs_df),
        "viewed_products": most_viewed_products(logs_df),
        "watched_items": frequently_watched_items(logs_df),
    }
