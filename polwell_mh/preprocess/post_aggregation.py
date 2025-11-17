"""
post_aggregation.py

Purpose:
    Loads all filtered Bluesky firehose Parquet files and performs a deduplication-style
    aggregation of posts. The script groups posts by their core identifiers
    (post_id, post_cid, author, createdAt, type, text) to produce a unique set
    of posts from the filtered dataset.

    This step is intended to prepare a clean, aggregated table of unique posts
    for subsequent processing (e.g., computing repost statistics or engagement
    metrics in later steps).

Inputs:
    Reads from:
        /scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/raw/filtered/*

Outputs:
    Writes a single Parquet file containing the aggregated (grouped) posts to:
        /scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/interim/aggregates/aggregate-0001.parquet

Usage:
    Run this script after the filtering stage to produce a unique/aggregated
    post-level dataset.
"""

import glob

import duckdb
from loguru import logger


def main():
    # Define aggregation query

    paths = glob.glob(
        "/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/raw/filtered/*.parquet"
    )

    valid_paths = []

    for p in paths:
        try:
            duckdb.sql(f"SELECT * FROM read_parquet('{p}') LIMIT 1").fetchall()
            valid_paths.append(p)
        except:
            logger.warning(f"Skipping corrupted parquet: {p}")
    logger.info(f"Found {len(valid_paths)} valid parquet files out of {len(paths)} total.")

    QUERY = f"""
    SELECT DISTINCT
        post_id,
        post_cid,
        author,
        createdAt,
        type,
        text
    FROM read_parquet({valid_paths})
    """

    # Connect directly to DuckDB database
    conn = duckdb.connect()
    # count = conn.execute("SELECT COUNT(*) FROM read_parquet('/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/raw/filtered/*')").fetchone()[0]
    # logger = duckdb.get_logger()
    # logger.set_level(duckdb.DuckDBLogLevel.DEBUG)
    # logger.info(f"Total number of rows in input data: {count}")
    # Enable progress bar
    conn.execute("SET enable_progress_bar = true")
    # Use all available threads
    conn.execute("PRAGMA threads=24")

    # Set output file path
    output_file = "/scratch/cs/ecanet/polwell-mental-health/polwell_mh/data/interim/aggregates/aggregate-0001.parquet"

    # Execute and save query directly to Parquet
    conn.execute(f"COPY ({QUERY}) TO '{output_file}' (FORMAT parquet)")

    # Close connections
    conn.close()


if __name__ == "__main__":
    main()
