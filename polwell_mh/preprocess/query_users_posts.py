"""
query_user_posts_fire.py

Purpose:
    Extracts all posts made by a given list of Bluesky usernames
    from one or more firehose NDJSON files using DuckDB.

Usage:
    python query_user_posts_fire.py \
        --input "/data/firehose/*.ndjson.gz" \
        --users /path/to/users.json \
        --output /output/dir/user_posts.parquet
"""

import json
from pathlib import Path
import re

import duckdb
import fire


def query_user_posts(input: str, users: str, output: str):
    """
    Extract posts authored by specific Bluesky users.

    Args:
        input: Path or glob pattern to .ndjson.gz firehose file(s).
               Example: "/data/firehose/*.ndjson.gz"
        users: Path to a JSON file containing a list of usernames.
               Example: "./target_users.json"
        output: Path to output Parquet file.
                Example: "/output/dir/user_posts.parquet"
    """

    # --- Load usernames ---

    with open(users, "r") as f:
        data = json.load(f)

    # Extract usernames from dictionary keys
    if not isinstance(data, dict):
        raise ValueError("Expected JSON to be a dictionary where keys are usernames.")

    usernames = list(data.keys())

    print(f"Loaded {len(usernames)} usernames.")
    # --- Ensure output directory exists ---
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Extract date from input for logging ---
    match = re.search(r"(\d{4}-\d{2}-\d{2})", input)
    date_str = match.group(1) if match else "combined"
    print(f"Processing firehose files for date: {date_str}")

    # --- DuckDB setup ---
    conn = duckdb.connect()
    conn.execute("PRAGMA threads=8")

    # --- Query parameters ---
    # MIN_TEXT_LENGTH = 15
    LANGUAGE_TEXT = "en"
    usernames_str = ", ".join(f"'{u}'" for u in usernames)
    input_path = input

    # Set output file path
    # Extract the date (YYYY-MM-DD) from the input path
    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)
    if not match:
        raise ValueError("Could not extract date (YYYY-MM-DD) from input path.")
    # --- Query ---
    QUERY = f"""
    WITH raw_data AS (
        SELECT *
        FROM read_ndjson(
            ['{input_path}'],
            columns = {{
                'action':    'VARCHAR',
                'type':      'VARCHAR',
                'author':    'VARCHAR',
                'createdAt': 'VARCHAR',
                'uri':       'VARCHAR',
                'cid':       'VARCHAR',
                'text':      'VARCHAR',
                'langs':     'VARCHAR[]',

            }},
            union_by_name = true
        )
    )
    SELECT DISTINCT
        author,
        createdAt,
        type,
        uri AS post_id,
        cid AS post_cid,
        text,
        langs
    FROM raw_data
    WHERE author IN ({usernames_str})
      AND list_contains(langs, '{LANGUAGE_TEXT}')
    ORDER BY createdAt
    """

    # --- Execute and save ---
    print("Running DuckDB query...")
    conn.execute(f"COPY ({QUERY}) TO '{output_path}' (FORMAT PARQUET)")
    conn.close()

    print(f"✅ Successfully saved user posts to {output_path}")


if __name__ == "__main__":
    fire.Fire(query_user_posts)
