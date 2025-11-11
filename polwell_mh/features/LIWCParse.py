
# coding: utf-8

from pathlib import Path
import string
import sys, os
from loguru import logger
from tqdm import tqdm

from polwell_mh.config import LEXICON_DIR, PROCESSED_DATA_DIR

import numpy as np
import pandas
#import matplotlib.pyplot as plt

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
        
    if isNormalized:
        # words_count = len(txtStr.split(' '))
        words_count = len(word_tokenize(txtStr))
        countArr = [x/words_count for x in countArr]

    return countArr
#%%

txtStr = "That looks like a Google Drive link — do you want to connect Google Drive to Slack? You’ll be able to preview files, manage access to documents, get notified about and reply to comments, and see when new files are shared with you."

print(getLiwcVector(txtStr, True))
print(getLiwcVector(txtStr, False))


def parseLiwcDF(input_df, target_col, save_path=None):
    liwcVectorList = []

    if input_df.empty:
        logger.warning("Input DataFrame is empty — returning empty DataFrame.")
        return input_df.copy()

    for i, txt in enumerate(input_df[target_col].values, start=1):
        if i % 200 == 0:
            print(i)
        liwcVector = getLiwcVector(txt, True)
        liwcVectorList.append(liwcVector)

    liwcDF = pandas.DataFrame(np.row_stack(liwcVectorList))
    validCatIdxs = liwcCatDF.catIdx.values - 1
    liwcDF = liwcDF[validCatIdxs]
    liwcDF.columns = liwcCatDF.catName.values
    liwcDF = pandas.concat([input_df, liwcDF], axis=1)

    if save_path is not None:
        liwcDF.to_csv(save_path, index=False)
    return liwcDF




#postsDF = pandas.read_csv("input/GPTCleanDF_1711610298.06188.csv")
#postsLiwcDF = parseLiwcDF(postsDF, 'PostText')
#postsLiwcDF.to_csv(PROCESSED_DATA_DIR / "/postsLiwcDF_"+str(time.time())+".csv", index = False)


