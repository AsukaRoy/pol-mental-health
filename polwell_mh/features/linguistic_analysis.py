"""
Linguistic analysis feature extraction.
"""

import re

from pathlib import Path
from venv import logger
import fire

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.util import ngrams
from polwell_mh.config import PROCESSED_DATA_DIR

import textstat
import string

import pandas as pd
from tqdm import tqdm

STOP_WORDS = set(stopwords.words("english"))


def repeatability(corpus: str) -> float:
    # calculate the normalized occurances of non-unique words
    # in the corpus
    token = word_tokenize(corpus)
    token = [i.lower() for i in token if i.lower() not in STOP_WORDS]

    if len(set(token)) == 0:
        # return nan
        return 0.0
    return len(token) / len(set(token))


def complexity(corpus: str) -> float:
    # and complexity as the average number of words per sentence
    word_count = len(corpus.split())
    sentence_count = textstat.sentence_count(corpus)
    if sentence_count == 0:
        # return nan
        return 0.0
    return word_count / sentence_count


def readability(corpus: str) -> float:
    return textstat.coleman_liau_index(corpus)


def main(input_path: str, text_column: str, output_path: Path = PROCESSED_DATA_DIR):
    logger.info(f"Loading input DataFrame from: {input_path}")
    input_df = pd.read_parquet(input_path)

    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)
    date_str = match.group(1) if match else "unknown_date"
    logger.info(f"Calculating linguistic analysis features for date: {date_str}")
    input_df["repeatability"] = input_df[text_column].progress_apply(repeatability)
    input_df["complexity"] = input_df[text_column].progress_apply(complexity)
    input_df["readability"] = input_df[text_column].progress_apply(readability)
    logger.info(f"Saving linguistic analysis features to: {output_path}")
    input_df.to_parquet(
        output_path / f"linguistic_analysis/linguistic_analysis_{date_str}.parquet",
        index=False,
    )


if __name__ == "__main__":
    fire.Fire(main)
