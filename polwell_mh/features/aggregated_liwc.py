'''
    Module to aggregate LIWC categories into broader features.
'''

import re
from pathlib import Path
from loguru import logger
import numpy as np
import pandas as pd
import fire
from tqdm import tqdm

from polwell_mh.config import PROCESSED_DATA_DIR


def aggregate_liwc_categoires(df):
    '''
    1) Cognition & Perception (cause,
    certain, cognitive, discrepancies, tentativeness, percep-
    tion, see, hear, feel, insight)

    (3) Lexical Density & Awareness (adverbs,article, verbs, auxiliary verbs, conjunctions, 
    inclusive, exclusive,
    preposition, negation, quantifer, relative) 
    (4) Interpersonal Focus (1st personal pronouns, 2nd personal pronouns, Impersonal pro-
    nouns) 
    (5) Temporal References (future, past, present).
    '''

    df["LIWC:Affective"] = df.apply(
        lambda row: sum(
            row[[
                "affect",   # same name
            ]]
        ),
        axis=1
    )

    df["LIWC:cognition_perception"] = df.apply(
        lambda row: sum(
            row[[
                "cogmech",    # same name
                "percept",    # same name

            ]]
        ),
        axis=1
    )


    # Social Context
    # Removed "humans" (not in columns), used "bio" for "biological processes", "friend" for "friends", "relig" for "religion", etc.
    

    df["LIWC:social_context"] = df.apply(
        lambda row: sum(
            row[[
                "bio",      # "biological processes"
                "social",    # "social"
                "work",      # "work"
                "achiev",    # "achievement"
                "home",      # "home"
                'leisure',    # "leisure"
                "money",     # "money"
                "relig",     # "religion"
                'death',    # "death"
            ]]
        ),
        axis=1
    )

    df["LIWC:biological"] = df.apply(
        lambda row: sum(
            row[[
                "bio",       # "biological processes"
            ]]
        ),
        axis=1
    )

    # Lexical Density / Awareness
    # Removed "inclusive" and "exclusive" (not in columns), renamed "adverbs" -> "adverb", "verbs" -> "verb", "auxiliary verbs" -> "auxverb", etc.
    df["LIWC:lexical_density_awareness"] = df.apply(
        lambda row: sum(
            row[[
                "article",   # "article"
                "prep",      # "preposition"
                "conj",      # "conjunctions"
                "adverbs",    # "adverbs"
                "negate",    # "negation"
                "auxvb",   # "auxiliary verbs"
                "verbs",      # "verbs"
                "quant",     # "quantifier"
                "relativ"    # "relative"
            ]]
        ),
        axis=1
    )

    # Interpersonal Focus
    # 1st personal pronouns -> ("i", "we"), 2nd -> ("you"), Impersonal -> ("ipron")
    df["LIWC:interpersonal_focus"] = df.apply(
        lambda row: sum(
            row[[
                "i",
                "we",
                "you",
                "ipron"
            ]]
        ),
        axis=1
    )
 
    # Temporal References
    # "future" -> "focusfuture", "past" -> "focuspast", "present" -> "focuspresent"
    df["LIWC:temporal_references"] = df.apply(
        lambda row: sum(
            row[[
                "future",
                "past",
                "present"
            ]]
        ),
        axis=1
    )

    return df

def main(input_path: str, output_path: str = PROCESSED_DATA_DIR):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)

    if not match:
        raise ValueError("Could not extract date (YYYY-MM-DD) from input path.")
    date_str = match.group(1)

    logger.info(f"Loading with pandas.read_parquet. : {input_path}")
    input_df = pd.read_parquet(input_path)

    if input_df.empty:
        logger.warning("Input DataFrame is empty — exiting.")
        return
    logger.info(f"Aggregating LIWC categories.")
    output_df = aggregate_liwc_categoires(input_df)
    # drop text column to reduce size
    output_file_path = output_path / f"liwc_aggregated_{date_str}.parquet"
    logger.info(f"Saving aggregated LIWC features to: {output_file_path}")
    output_df.to_parquet(output_file_path, index=False)

if __name__ == "__main__":
    fire.Fire(aggregate_liwc_categoires)