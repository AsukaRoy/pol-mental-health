import pytest
import pandas as pd
import tempfile
import os
from polwell_mh.features.behaviors import summarize_user_actions    # <-- replace with your actual module name

@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample Bluesky user actions."""
    sample_data = pd.DataFrame([
        {"author": "did:plc:user1", "type": "app.bsky.feed.post"},
        {"author": "did:plc:user1", "type": "app.bsky.feed.post"},
        {"author": "did:plc:user1", "type": "app.bsky.feed.repost"},
        {"author": "did:plc:user2", "type": "app.bsky.graph.follow"},
        {"author": "did:plc:user2", "type": "app.bsky.feed.like"},
        {"author": "did:plc:user3", "type": "app.bsky.feed.post"},
        {"author": "did:plc:user3", "type": "app.bsky.feed.like"},
    ])

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    sample_data.to_csv(temp_file.name, index=False)
    yield temp_file.name
    os.remove(temp_file.name)


def test_summarize_user_actions_counts(sample_csv_file):
    """Test that the function correctly counts posts, reposts, follows, and likes."""
    summary = summarize_user_actions(sample_csv_file)
    print(summary)
    
    expected = pd.DataFrame({
        "author": ["did:plc:user1", "did:plc:user2", "did:plc:user3"],
        "posts": [2, 0, 1],
        "reposts": [1, 0, 0],
        "follows": [0, 1, 0],
        "likes": [0, 1, 1]
    })

    # Sort to ensure deterministic comparison
    summary_sorted = summary.sort_values("author").reset_index(drop=True)
    expected_sorted = expected.sort_values("author").reset_index(drop=True)

    pd.testing.assert_frame_equal(summary_sorted, expected_sorted)


def test_missing_columns_raises_error(tmp_path):
    """Test that the function raises ValueError when required columns are missing."""
    invalid_data = pd.DataFrame({"type": ["app.bsky.feed.post"]})
    invalid_file = tmp_path / "invalid.csv"
    invalid_data.to_csv(invalid_file, index=False)

    with pytest.raises(ValueError, match="Missing columns"):
        summarize_user_actions(str(invalid_file))