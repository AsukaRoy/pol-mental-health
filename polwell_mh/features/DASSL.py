import pickle
import numpy as np
import pandas as pd

from polwell_mh.config import DASSL_CLASSIFIER_DIR

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import string

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
        self.dassTypes = ["anxiety", "stress", "depression", "suicide", "psychosis", 'loneliness']
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