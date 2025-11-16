

import polwell_mh
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pathlib import Path

# Import the class to test
from polwell_mh.features.DASSL import LoadDASSClassifiers


@pytest.fixture
def mock_vectorizer_classifier():
    """Create mock vectorizer and classifier objects."""
    mock_vectorizer = MagicMock()
    mock_vectorizer.transform.return_value = "mock_transformed_text"

    mock_classifier = MagicMock()
    mock_classifier.predict.return_value = ["mock_prediction"]

    return mock_vectorizer, mock_classifier


import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_vectorizer_classifier():
    """Create mock vectorizer and classifier objects for testing."""
    mock_vectorizer = MagicMock()
    mock_vectorizer.transform.return_value = "mock_features"

    mock_classifier = MagicMock()
    mock_classifier.predict.return_value = [1]

    return mock_vectorizer, mock_classifier


@pytest.fixture
def mock_joblib_load(mock_vectorizer_classifier):
    """Patch joblib.load to return mock vectorizers and classifiers."""
    vectorizer, classifier = mock_vectorizer_classifier

    def _mock_load(path):
        if "Vectorizer" in str(path):
            return vectorizer
        elif "Classifier" in str(path):
            return classifier
        else:
            raise ValueError(f"Unexpected path: {path}")

    with patch("joblib.load", side_effect=_mock_load) as mock_load:
        yield mock_load


def test_initialization_loads_all_classifiers(mock_joblib_load):
    """Test that all vectorizers and classifiers are loaded for each DASS type."""
    dassl = LoadDASSClassifiers()

    expected_types = ["anxiety", "stress", "depression", "suicide", "psychosis", "loneliness"]
    assert set(dassl.dassTypes) == set(expected_types)
    assert len(dassl.ngVectorizers_dic) == len(expected_types)
    assert len(dassl.classifers_dic) == len(expected_types)

    for k, v in dassl.ngVectorizers_dic.items():
        assert v is not None
    for k, v in dassl.classifers_dic.items():
        assert v is not None


def test_returnDASSAnno_returns_expected_predictions(mock_joblib_load):
    """Test that returnDASSAnno returns predictions for each DASS category."""
    dassl = LoadDASSClassifiers()
    text = "I feel sad and anxious."

    result = dassl.returnDASSAnno(text)
    assert isinstance(result, list)
    assert len(result) == len(dassl.dassTypes)
    for r in result:
        assert r == [1]  # from our MagicMock return value


def test_returnDASSClassification_adds_columns(mock_joblib_load):
    """Test that DASS classification adds expected columns to dataframe."""
    dassl = LoadDASSClassifiers()
    df = pd.DataFrame({"text": ["I am feeling fine today.", "I am very stressed."]})

    out_df = dassl.returnDASSClassifiction(df.copy(), "text")
    print(out_df)
    # Ensure the new DASS columns exist
    for dassType in dassl.dassTypes:
        assert f"DASS_{dassType}" in out_df.columns
        assert all(out_df[f"DASS_{dassType}"] == 1)  # from mock prediction


def test_vectorizer_transform_called_correctly(mock_joblib_load):
    """Ensure vectorizer.transform is called with the correct text."""
    dassl = LoadDASSClassifiers()
    text = "Example text"

    # access first mock vectorizer
    vectorizer = list(dassl.ngVectorizers_dic.values())[0]
    dassl.returnDASSAnno(text)
    vectorizer.transform.assert_called_with([text])
