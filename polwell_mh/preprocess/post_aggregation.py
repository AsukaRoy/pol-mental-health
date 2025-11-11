"""
post_aggregation.py

Purpose:
    Aggregates repost counts for each post from previously filtered Bluesky firehose data.
    Reads all filtered Parquet files, groups posts by post ID, target (original author), and text,
    then counts the number of reposts per post. Outputs the results as a single Parquet file.

Inputs:
    Reads from: /m/cs/scratch/ecanet/bluesky_datapool/filtered/*/*

Outputs:
    Writes to: /m/cs/scratch/ecanet/bluesky_datapool/aggregates/aggregate-0001.parquet

Usage:
    Run as a standalone script after filtering step.
"""

import duckdb

def main():
    # Define aggregation query
    QUERY = """
    SELECT 
        post_id,
        target,
        text,
        COUNT(*) AS repost_count
    FROM read_parquet('/m/cs/scratch/ecanet/bluesky_datapool/raw_filtered/*/*')
    GROUP BY post_id, target, text
    ORDER BY repost_count DESC
    """

    # Connect directly to DuckDB database
    conn = duckdb.connect()
    
    # Enable progress bar
    conn.execute("SET enable_progress_bar = true")
    # Use all available threads
    conn.execute("PRAGMA threads=24")

    # Set output file path
    output_file = (
        "/m/cs/scratch/ecanet/bluesky_datapool/aggregates/aggregate-0001.parquet"
    )

    # Execute and save query directly to Parquet
    conn.execute(f"COPY ({QUERY}) TO '{output_file}' (FORMAT parquet)")

    # Close connections
    conn.close()


if __name__ == "__main__":
    main()
