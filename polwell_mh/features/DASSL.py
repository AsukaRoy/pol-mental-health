import pickle
import numpy as np
import pandas as pd

from polwell_mh.config import DASSL_CLASSIFIER_DIR
from polwell_mh.config import LEXICON_DIR, PROCESSED_DATA_DIR
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import string
import fire
import re
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_curve, auc
from sklearn import ensemble
from sklearn.ensemble import RandomForestClassifier

from loguru import logger

from sklearn import svm
import sklearn
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from collections import Counter

from tqdm import tqdm
from sklearn import multiclass

from nltk import word_tokenize
import pickle
import pytz

import multiprocessing as mp

# ModuleNotFoundError: No module named 'sklearn.svm.classes'
# from sklearn.svm import SVC

import sys
import sklearn.svm
from pathlib import Path
sys.modules["sklearn.svm.classes"] = sklearn.svm


class LoadDASSClassifiers:
    def __init__(self):
        self.dassTypes = [
            "anxiety", 
            "stress", 
            "depression", 
            "suicide", 
            "psychosis", 
            'loneliness'
            ]
        self.ngVectorizers_dic = {}

        self.classifers_dic = {}

        for i in self.dassTypes:
            ngVectorizer = joblib.load(
                DASSL_CLASSIFIER_DIR / (i + "NgVectorizer.pickle")
            )
            classifier = joblib.load(
                DASSL_CLASSIFIER_DIR / (i + "Classifier.pickle")
            )
            self.ngVectorizers_dic[i] = ngVectorizer
            self.classifers_dic[i] = classifier

    def returnDASSAnno(self, text):
        annotat_results = []
        for i in self.dassTypes:
            ngX = self.ngVectorizers_dic[i].transform([text])
            annotat_results.append(self.classifers_dic[i].predict(ngX))

        return annotat_results

    def returnDASSClassifiction(self, df, target_col):
        for dassType in self.dassTypes:

            print(dassType)
            ngVectorizer = self.ngVectorizers_dic[dassType]
            ngX = ngVectorizer.transform(df[target_col].values)

            print("Ng Trasformed", dassType)

            classifier = self.classifers_dic[dassType]
            df[f"DASS_{dassType}"] = classifier.predict(ngX)
        return df
    
def main(input_path: str, text_column: str, output_path: str = PROCESSED_DATA_DIR):
    dassl = LoadDASSClassifiers()

    match = re.search(r"(\d{4}-\d{2}-\d{2})", input_path)

    if not match:
        raise ValueError("Could not extract date (YYYY-MM-DD) from input path.")
    date_str = match.group(1)

    logger.info(f"Loading with pandas.read_parquet. : {input_path}")
    input_df = pd.read_parquet(input_path)

    if input_df.empty:
        logger.warning("Input DataFrame is empty — exiting.")
        return
    logger.info(f"Classifying DASSL features from column: {text_column}")
    output_df = dassl.returnDASSClassifiction(input_df, text_column)
    # drop text column to reduce size
    output_df = output_df.drop(columns=[text_column])

    logger.info(f"Saving DASSL classified DataFrame to: {output_path}")
    output_df.to_parquet(output_path / f"DASSL/postsDASSL_{date_str}.parquet", index=False)



if __name__ == "__main__":
    fire.Fire(main)