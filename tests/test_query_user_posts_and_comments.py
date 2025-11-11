"""
pytest test for `query_user_posts_and_comments.py`

Purpose:
    Compares DuckDB output from query_user_posts_and_comments.py with
    a pandas ground truth, using a small random sample of users from
    one firehose NDJSON file.

Run manually:
    pytest -v tests/test_query_user_posts_and_comments.py \
        --input /path/to/firehose-YYYY-MM-DD.ndjson.gz \
        --script /path/to/query_user_posts_and_comments.py \
        --output /tmp/test_output.parquet
"""

import gzip
import json
import subprocess
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
import pytest


def load_firehose_records(input_path: Path, limit: int = 50000):
    """Read a gzipped NDJSON file safely, up to a limit of lines."""
    records = []
    with gzip.open(input_path, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip malformed lines
            if i >= limit:
                break
    if not records:
        raise ValueError("No valid JSON records found in the NDJSON file!")
    return pd.DataFrame(records)


@pytest.mark.parametrize("n_users", [3])
def test_query_user_posts_and_comments(tmp_path, n_users, request):
    """
    Compare DuckDB query results vs. pandas filtering for a sample of users.
    """

    # --- Command-line style arguments via pytest CLI options ---
    input_file = request.config.getoption("--input")
    script_path = request.config.getoption("--script")
    output_file = request.config.getoption("--output")

    if not input_file or not script_path or not output_file:
        pytest.skip("Skipping test: --input, --script, or --output not provided.")

    input_path = Path(input_file)
    output_path = Path(output_file)
    script_path = Path(script_path)

    print(f"\n🔍 Loading firehose sample from {input_path}")
    df = load_firehose_records(input_path)
    print(f"✅ Loaded {len(df)} records from {input_path}")

    # --- Prepare sample users ---
    df_posts = df.copy()
    users = (
        df_posts["author"]
        .dropna()
        .drop_duplicates()
        .sample(min(n_users, df_posts["author"].nunique()), random_state=42)
        .tolist()
    )

    print(f"✅ Sampled {len(users)} users: {users}")

    # --- Write temporary users.json ---
    tmp_userfile = tmp_path / "test_users.json"
    with open(tmp_userfile, "w") as f:
        json.dump(users, f)

    # --- Run DuckDB query script ---
    cmd = [
        "python",
        str(script_path),
        "--input", str(input_path),
        "--users", str(tmp_userfile),
        "--output", str(output_path),
    ]
    print("🚀 Running DuckDB query script...")
    subprocess.run(cmd, check=True)
    assert output_path.exists(), "Output Parquet file was not created."
    print(f"✅ Script finished, output saved to {output_path}")

    # --- Load DuckDB result ---
    duckdb_output = pd.read_parquet(output_path)
    print(f"Loaded {len(duckdb_output)} rows from DuckDB output.")

    # --- Pandas baseline filtering (mirror DuckDB logic) ---
    ref = df_posts[df_posts["author"].isin(users)].copy()
    ref = ref[ref["langs"].apply(lambda x: isinstance(x, list) and "en" in x)]
    ref = ref.loc[:, ["author", "createdAt", "uri", "cid", "text", "langs"]]
    ref = ref.rename(columns={"uri": "post_id", "cid": "post_cid"})

    # --- Compare ---
    merged = duckdb_output.merge(
        ref, on=["author", "post_id", "post_cid"], how="outer", indicator=True
    )

    n_only_duckdb = (merged["_merge"] == "left_only").sum()
    n_only_pandas = (merged["_merge"] == "right_only").sum()
    print("\n🔎 Comparison summary:")
    print(f"  Rows only in DuckDB output: {n_only_duckdb}")
    print(f"  Rows only in Pandas ref:    {n_only_pandas}")
    print(f"  Rows matched:               {(merged['_merge'] == 'both').sum()}")

    if n_only_duckdb or n_only_pandas:
        print("\n🟠 Mismatched rows (first few):")
        print(merged[merged["_merge"] != "both"].head())

    # --- Assertion ---
    assert n_only_duckdb == 0 and n_only_pandas == 0, (
        f"Mismatch detected: {n_only_duckdb} only in DuckDB, "
        f"{n_only_pandas} only in pandas reference."
    )


# --- Add pytest CLI options ---
def pytest_addoption(parser):
    parser.addoption("--input", action="store", help="Path to firehose .ndjson.gz file")
    parser.addoption("--script", action="store", help="Path to query_user_posts_and_comments.py")
    parser.addoption("--output", action="store", help="Output Parquet file path")
