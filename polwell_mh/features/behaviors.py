import pandas as pd

def summarize_user_actions(csv_path: str) -> pd.DataFrame:
    """
    Summarize user actions from a Bluesky dataset CSV file.

    Parameters:
    ----------
    csv_path : str
        Path to the CSV file containing Bluesky actions.

    Returns:
    -------
    pd.DataFrame
        DataFrame with counts of posts, reposts, follows, and likes for each user.
    """
    # Load data
    df = pd.read_csv(csv_path)

    # Ensure expected columns exist
    required_columns = {"author", "type"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Define mapping of action types
    action_map = {
        "app.bsky.feed.post": "posts",
        "app.bsky.feed.repost": "reposts",
        "app.bsky.graph.follow": "follows",
        "app.bsky.feed.like": "likes"
    }

    # Filter only known types
    df = df[df["type"].isin(action_map.keys())]

    # Map each action to a category (post, repost, follow, like)
    df["action_category"] = df["type"].map(action_map)

    # Count number of actions per author and category
    summary = (
        df.groupby(["author", "action_category"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    summary.columns.name = None  # ✅ removes 'action_category'
    # Ensure all expected columns exist; fill missing with zeros
    for col in action_map.values():
        if col not in summary.columns:
            summary[col] = 0

    return summary[["author", "posts", "reposts", "follows", "likes"]]