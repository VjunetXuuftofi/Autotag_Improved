"""
Copyright 2016 Thomas Woodside

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Provides tools for machine learning new autotags.
"""
import re
import pickle
import pandas as pd
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectPercentile
from sklearn.grid_search import GridSearchCV
import os

stemmer = SnowballStemmer(
    "english")  # This is done in the main body to avoid redundancy


def modify(description):
    """
    :param description: Text description of loan.
    :return: Cleaned description ready to be vectorized.
"""
    words = ""
    description = nltk.wordpunct_tokenize(description)
    for word in description:
        word = word.replace(" ", "")
        word = re.sub("[0-9]", "#", word)
        words += stemmer.stem(word) + " "
    words = words[:-1]
    return words


def initializefeatures(filename, toread):
    """
    Write a csv containing numpy arrays of the cleaned descriptions.
    :param filename: The name of the file to initialize the features from.
    :param toread: The type of description to initialize features from. Either
    "Description" or "Use"
    """
    data = pd.read_csv(filename)
    data = data[data.Description.notnull()]
    data = data[data.Use.notnull()]
    print(data)
    features = []
    for index in tqdm(range(0, len(data))):
        thisfeature = data.iloc[index]
        try:
            features.append(modify(thisfeature[toread]))
        except:
            print(features[index - 1])
    pickle.dump(pd.Series(features), open(filename[:-4] + "features" + toread,
                                    "wb+"))


def initialize(filename, labels_train, typetoread, toexclude=None,
               n_estimators=None, estimators_to_test=None,
               class_weight=None):
    """
    Takes in features and labels pertaining to a tag and fits and returns a
    TfidfVectorizer, SelectPercentile, and RandomForestClassifier
    :param filename: The base file location where information about the dataset
     can be found.
    :param labels_train: The labels to use when classifying.
    :param typetoread: The features list to use ("Use" or "Description")
    :param toexclude: A list of indices of the features list to exclude from
    classification. Useful to exclude values known to be positive or
    negative without classifier use. If not given, assumes all features are
    valid.
    :param n_estimators: The number of trees to use in the Random Forest
    Classifier as per the sklearn documentation. If not given, GridSearchCV
    will select between 50, 150, and 250.
    :param estimators_to_test: A list of different numbers of estimators to
    test using GridSearch CV as per the sklearn documentation. If not given,
    GridSearchCV will select between 50, 150, and 250.
    :param class_weight: The weightings to use for the various classes as
    per the sklearn documentation. If not given, all classes have equal weight
    :return forest: A fitted RandomForestVectorizer.
    :return vectorizer: A fitted TfidfVectorizer.
    :return selector: A fitted Selector at 10%.
    """

    features_train = pickle.load(open(
        os.path.abspath("./DataFiles/" + filename +
        "features" + typetoread),
        "rb"))
    labels_train = pd.Series(labels_train)
    if toexclude:
        features_train = pd.Series(
            np.delete(np.array(features_train), toexclude, axis=0))
    print("Creating Vectorizer")
    vectorizer = TfidfVectorizer(stop_words="english",
                                 max_df=.5,
                                 ngram_range=(1, 3))
    print("Fitting Vectorizer")
    features_train_transformed = vectorizer.fit_transform(features_train)
    print("Creating Selector")
    selector = SelectPercentile()
    print("Fitting Selector")
    selector.fit(features_train_transformed,
                 labels_train)
    print("Transforming data")
    features_train_transformed_selected = selector.transform(
        features_train_transformed).toarray()
    print("Creating Forest")
    if not n_estimators:
        forest = RandomForestClassifier(min_samples_leaf=2,
                                        class_weight=class_weight)
        if not estimators_to_test:
            parameters = {
                "n_estimators": [50, 150, 250],
            }
        else:
            parameters = {
                "n_estimators": estimators_to_test,
            }
        forest = GridSearchCV(forest,
                              parameters)
    else:
        forest = RandomForestClassifier(n_estimators=n_estimators,
                                        min_samples_leaf=2,
                                        class_weight=class_weight)
    print("Fitting Forest")
    forest.fit(features_train_transformed_selected,
               labels_train)
    return forest, vectorizer, selector

if __name__ == "__main__":
    initializefeatures("../AutoTag/"
                       "DataFiles/loans_assigned_for_tagging_with_descriptions"
                       "_combined5.csv", "Use")
    initializefeatures("../AutoTag/"
                       "DataFiles/loans_assigned_for_tagging_with_descriptions"
                       "_combined5.csv", "Description")