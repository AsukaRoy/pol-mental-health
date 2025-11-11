"""
Unit tests for polwell_mh.LIWCParse
Run with:
    pytest -v tests/test_liwcparse.py
"""

import pandas as pd
import numpy as np
import pytest
from pathlib import Path

import polwell_mh.features.LIWCParse as liwc


@pytest.fixture(scope="session")
def sample_text():
    """Example text for LIWC parsing."""
    return "I am happy today but was sad yesterday."


@pytest.fixture(scope="session")
def sample_df():
    """A small DataFrame for parseLiwcDF testing."""
    return pd.DataFrame({
        "id": [1, 2],
        "text": ["I am happy", "This is sad"]
    })


def test_liwc_files_exist():
    """Ensure required LIWC lexicon files exist in LEXICON_DIR."""
    assert liwc.categoriesmap_file.exists(), f"Missing file: {liwc.categoriesmap_file}"
    assert liwc.dictionary_file.exists(), f"Missing file: {liwc.dictionary_file}"


def test_getLiwcVector_returns_correct_length(sample_text):
    """getLiwcVector() should return a list of length = number of LIWC categories."""
    vec = liwc.getLiwcVector(sample_text, isNormalized=False)
    assert isinstance(vec, list)
    assert len(vec) == max(liwc.catRegexDict.keys())
    # Values should be non-negative
    assert all(x >= 0 for x in vec)


def test_getLiwcVector_normalization(sample_text):
    """Normalized vector should have smaller total magnitude than raw counts."""
    raw_vec = np.array(liwc.getLiwcVector(sample_text, False))
    norm_vec = np.array(liwc.getLiwcVector(sample_text, True))

    # Normalized values should be strictly smaller or equal (except all zeros)
    assert sum(norm_vec) < sum(raw_vec) or np.isclose(sum(norm_vec), 0)
    assert all(n <= r for n, r in zip(norm_vec, raw_vec))



def test_parseLiwcDF_output_structure(sample_df, tmp_path):
    """parseLiwcDF() should output DataFrame with original + LIWC columns."""
    save_path = tmp_path / "liwc_output.csv"
    df_out = liwc.parseLiwcDF(sample_df, target_col="text", save_path=save_path)

    # ✅ Should be a DataFrame with expected columns
    assert isinstance(df_out, pd.DataFrame)
    for col in ["id", "text"]:
        assert col in df_out.columns

    # ✅ LIWC categories should appear as columns
    for col_name in liwc.liwcCatDF.catName.head(5):  # check a few
        assert col_name in df_out.columns, f"Missing LIWC column: {col_name}"

    # ✅ Save path should exist
    assert save_path.exists()
    df_saved = pd.read_csv(save_path)
    assert list(df_saved.columns) == list(df_out.columns)
    assert len(df_saved) == len(sample_df)


def test_parseLiwcDF_handles_empty_dataframe(tmp_path):
    """parseLiwcDF() should gracefully handle empty DataFrame."""
    empty_df = pd.DataFrame({"id": [], "text": []})
    df_out = liwc.parseLiwcDF(empty_df, "text")
    assert df_out.empty
