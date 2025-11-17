
# coding: utf-8

from pathlib import Path
import string
import sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
import fire

from loguru import logger
from tqdm import tqdm

from polwell_mh.config import LEXICON_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas
#import matplotlib.pyplot as plt
import gzip
import json
import re
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize, sent_tokenize
import nltk
nltk.download('punkt_tab')

categoriesmap_file = LEXICON_DIR / "LIWC2015_categoriesMap.txt"
dictionary_file = LEXICON_DIR / "LIWC2015_dict.txt"

logger.info(f"LIWC categories map file path: {categoriesmap_file}")
logger.info(f"LIWC dictionary file path: {dictionary_file}")


liwcCatDF = pandas.read_csv(categoriesmap_file, sep="\t", names = ["catIdx", "catName"])

liwcIdxCatDict = dict(zip(liwcCatDF.catIdx, liwcCatDF.catName))

liwcIdxCatDict.keys
	
#liwcDictDF = os.path.join("", "data/liwc2015_dict.txt")

numCats = max(liwcCatDF.catIdx.values)

# liwcCatList = [list()]*numCats
catKeywordsDict = dict()

with open(dictionary_file, "r") as file_handle:
    for line in file_handle:
        lexicon_item = line.strip().split("\t")
        keyword = lexicon_item[0]
        for catIdx in lexicon_item[1:]:
            idx = int(catIdx)
            # print(idx, keyword)
            if idx in catKeywordsDict:
                tempList = catKeywordsDict[idx]
            else:
                tempList = list()
            tempList.append(keyword)
            catKeywordsDict[idx] = tempList
            

catRegexDict = dict()

for idx, keywordsList in catKeywordsDict.items():
    #print(idx, keywordsList)
    lexicon_str = "("
    for item in keywordsList:
        if "*" in item:
            item = r"\b{0}\b".format(item.replace("*", ".*?"))
        else:
            item = r"\b{0}\b".format(item)
            lexicon_str += item + "|"
    lexicon_str = lexicon_str[:-1] + ")"
    #print(lexicon_str)
    catRegexDict[idx]=lexicon_str

#%%

def getLiwcVector(txtStr, isNormalized):
    txtStr = txtStr.lower()
    countArr = [0]*max(catRegexDict.keys())

    for idx, patternStr in catRegexDict.items():
        pattern = re.compile(patternStr)
        count = len(pattern.findall(txtStr))
        # if(count!=0):
        #     print(liwcCatDF[liwcCatDF.catIdx==idx].catName.values[0], count)
        countArr[idx-1]=count
        # add word count as the last element
        # countArr.append(len(word_tokenize(txtStr)))
        
    if isNormalized:
        # words_count = len(txtStr.split(' '))
        words_count = len(word_tokenize(txtStr))
        countArr = [x/words_count for x in countArr]

    return countArr
#%%

txtStr = "That looks like a Google Drive link — do you want to connect Google Drive to Slack? You’ll be able to preview files, manage access to documents, get notified about and reply to comments, and see when new files are shared with you."

logger.info(getLiwcVector(txtStr, True))
logger.info(getLiwcVector(txtStr, False))


def parseLiwcDF(input_df: pandas.DataFrame, target_col: str, isNormalized: bool = False) -> pandas.DataFrame:
    liwcVectorList = []

    if input_df.empty:
        logger.warning("Input DataFrame is empty — returning empty DataFrame.")
        return input_df.copy()

    for i, txt in enumerate(input_df[target_col].values, start=1):
        if i % 200 == 0:
            print(i)
        liwcVector = getLiwcVector(txt, isNormalized)
        liwcVectorList.append(liwcVector)

    liwcDF = pandas.DataFrame(np.row_stack(liwcVectorList))

    if not isNormalized:
        # add word count as the last column using apply
        input_df['wordCount'] = input_df[target_col].apply(lambda x: len(word_tokenize(x)))
        liwcDF['wordCount'] = input_df['wordCount'].values

    validCatIdxs = liwcCatDF.catIdx.values - 1
    liwcDF = liwcDF[validCatIdxs]
    liwcDF.columns = liwcCatDF.catName.values
    liwcDF = pandas.concat([input_df, liwcDF], axis=1)
    # drop text column to reduce size
    liwcDF = liwcDF.drop(columns=[target_col])
    #if save_path is not None:
    #    liwcDF.to_csv(save_path, index=False)
    return liwcDF


# read csv file and parse LIWC features
def run_parse_liwc(input_path: str, text_column: str, output_parquet: str = PROCESSED_DATA_DIR, n_threads: int = 1):


    # Set output file path
    # Extract the date (YYYY-MM-DD) from the input path
    
    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)

    if not match:
        raise ValueError("Could not extract date (YYYY-MM-DD) from input path.")
    date_str = match.group(1)

    logger.info("Loading with pandas.read_parquet. : {input_path}")
    input_df = pandas.read_parquet(input_path)
    # type == "app.bsky.feed.post"
    input_df = input_df[input_df['type'] == "app.bsky.feed.post"]
    
    if input_df.empty:
        logger.warning("Input DataFrame is empty — exiting.")
        return
    #test with smaller data
    # input_df = input_df.sample(n=5000, random_state=42)

    logger.info(f"Parsing LIWC features from column: {text_column}")
    # multi-threading can be implemented here if needed for performance

    # the shape of input_df
    logger.info(f"Input DataFrame shape: {input_df.shape}")

    if n_threads <= 1:
        logger.info("Using a single thread for LIWC parsing.")
        liwc_df = parseLiwcDF(input_df, text_column)
    else:
        logger.info(f"Using {n_threads} threads for LIWC parsing.")
        # ------------------------
        # Multithreading section
        # ------------------------
        def process_chunk(df_chunk):
            return parseLiwcDF(df_chunk, text_column)

        # split the dataframe into n roughly equal pieces
        chunks = np.array_split(input_df, n_threads)
        results = []

        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

            for future in as_completed(futures):
                results.append(future.result())

        # combine back into single df
        liwc_df = pandas.concat(results, ignore_index=True)


    #logger.info(f"Saving output CSV file with LIWC features: {output_csv}")
    #liwc_df.to_csv(str(output_csv) + "/postsLiwcDF_"+str(time.time())+".csv", index=False)
    # the shape of input_df
    logger.info(f"liwc_df DataFrame shape: {liwc_df.shape}")
    # save as parquet
    logger.info(f"Saving output Parquet file with LIWC features: {output_parquet}")
    liwc_df.to_parquet(output_parquet / f"LIWC/postsLiwcDF_{date_str}.parquet", index=False)
    # logger outdf info
    logger.info(f"Output DataFrame info:\n{liwc_df.info()}")

    # logger statistics using df.describe()
    desc = liwc_df.describe()
    logger.info(f"LIWC feature counts description:\n{desc}")
    #logger.info("LIWC feature counts summary:")

    logger.info(f"Output DataFrame info:\n{liwc_df}")
    logger.info("LIWC parsing completed successfully.")

if __name__ == "__main__":
    fire.Fire(run_parse_liwc)


#postsDF = pandas.read_csv("input/GPTCleanDF_1711610298.06188.csv")
#postsLiwcDF = parseLiwcDF(postsDF, 'PostText')
#postsLiwcDF.to_csv(PROCESSED_DATA_DIR / "/LIWC/postsLiwcDF_"+str(time.time())+".csv", index = False)


