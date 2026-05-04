import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


def load_logs(file_path="sample_data.json"):
    """Read the sample JSON log file and return a pandas DataFrame."""
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    logs = raw_data.get("logs", [])
    dataframe = pd.DataFrame(logs)

    if dataframe.empty:
        return dataframe

    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
    dataframe["duration_seconds"] = dataframe["duration_seconds"].fillna(0).astype(int)
    return dataframe


def process_user_data(logs_df):
    """Group search, watch, wishlist, and view activity by user."""
    users = defaultdict(
        lambda: {
            "search_history": [],
            "watch_history": [],
            "wishlist": [],
            "view_history": [],
            "total_time_seconds": 0,
        }
    )

    for _, row in logs_df.iterrows():
        user_id = row["user_id"]
        action = row["action"]

        item = {
            "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "query": row.get("query", ""),
            "category": row.get("category", ""),
            "product_id": row.get("product_id", ""),
            "product_name": row.get("product_name", ""),
            "duration_seconds": int(row.get("duration_seconds", 0)),
        }

        if action == "search":
            users[user_id]["search_history"].append(item)
        elif action == "watch":
            users[user_id]["watch_history"].append(item)
        elif action == "wishlist":
            users[user_id]["wishlist"].append(item)
        elif action == "view":
            users[user_id]["view_history"].append(item)

        users[user_id]["total_time_seconds"] += item["duration_seconds"]

    return dict(users)


def get_user_ids(user_data):
    """Return available user IDs sorted alphabetically."""
    return sorted(user_data.keys())
