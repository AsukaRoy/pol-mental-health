import pytest
from pathlib import Path

# Default paths (adjust these to your setup)
DEFAULT_INPUT = "/m/cs/scratch/sinitaivas/bluesky_firehose/firehose_stream/2024-12-17/2024-12-17T21.ndjson.gz"
DEFAULT_SCRIPT = "/scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/query_users_posts.py"
DEFAULT_OUTPUT = str(Path("/tmp") / "test_user_posts.parquet")
DEFAULT_N_USERS = 10


def pytest_addoption(parser):
    parser.addoption("--input", action="store", default=DEFAULT_INPUT, help="Path to firehose .ndjson.gz file")
    parser.addoption("--script", action="store", default=DEFAULT_SCRIPT, help="Path to query_user_posts_and_comments.py")
    parser.addoption("--output", action="store", default=DEFAULT_OUTPUT, help="Output Parquet file path")
    parser.addoption("--n_users", type=int, default=DEFAULT_N_USERS, help="Number of random users to sample")
