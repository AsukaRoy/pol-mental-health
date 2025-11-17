"""
initial_query.py

Purpose:
    Processes Bluesky firehose data for a given day, extracting repost and post relationships using DuckDB.
    The script filters for English-language posts of at least N characters, joins them with corresponding reposts,
    and outputs the results as a Parquet file organized by date.

Usage:
    python initial_query.py --input /path/to/input-YYYY-MM-DD.ndjson.gz

Inputs:
    --input: Path to the .ndjson.gz firehose file for a specific date (YYYY-MM-DD).

Outputs:
    Parquet file containing repost relationships, saved to a date-based directory.
"""

import argparse
import duckdb
import re
from pathlib import Path


def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description="Process firehose data with DuckDB")
    parser.add_argument(
        "--input", required=True, help="Path to .ndjson.gz files for a specific day"
    )
    args = parser.parse_args()

    # Set input file path
    input_path = args.input

    # Set output file path
    # Extract the date (YYYY-MM-DD) from the input path
    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)
    if not match:
        raise ValueError("Could not extract date (YYYY-MM-DD) from input path.")
    date_str = match.group(1)

    # Define output directory and file
    output_dir = Path("/m/cs/scratch/ecanet/bluesky_datapool/raw_filtered") / date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{date_str}-filtered.parquet"

    print(f"Output will be written to: {output_file}")

    # Connect directly to DuckDB database
    conn = duckdb.connect()
    conn.execute("PRAGMA threads=8")

    # Query parameters
    MIN_TEXT_LENGTH = 15
    LANGUAGE_TEXT = "en"

    # Query template
    QUERY = f"""WITH raw_data AS (
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
        WHERE action = 'create'
    ),
    reposts AS (
        SELECT
            author AS reposting_author,
            subject->>'uri' AS post_id,
            subject->>'cid' AS post_cid,
            regexp_extract(subject->>'uri', 'at://(did:plc:[^/]+)', 1) AS original_author,
            createdAt AS repost_created_at
        FROM raw_data
        WHERE type = 'app.bsky.feed.repost'
    ),
    posts AS (
        SELECT
            author AS original_author,
            uri AS post_id,
            cid AS post_cid,
            text,
            langs
        FROM raw_data
        WHERE type = 'app.bsky.feed.post'
        AND length(text) >= {MIN_TEXT_LENGTH}
        AND langs IS NOT NULL
        AND list_contains(langs, '{LANGUAGE_TEXT}')
    )
    SELECT DISTINCT
        reposts.reposting_author AS source,
        posts.original_author AS target,
        posts.post_id,
        reposts.repost_created_at,
        posts.text,
        posts.langs
    FROM reposts
    INNER JOIN posts
        ON posts.post_id = reposts.post_id
    AND posts.post_cid = reposts.post_cid
    ORDER BY reposts.repost_created_at
    """

    # Execute and save query directly to Parquet
    conn.execute(f"COPY ({QUERY}) TO '{output_file}' (FORMAT parquet)")

    # Close connections
    conn.close()


if __name__ == "__main__":
    main()
