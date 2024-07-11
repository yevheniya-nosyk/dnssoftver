# Copyright 2023 Yevheniya Nosyk
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sklearn.model_selection
import sklearn.tree
import sklearn.metrics
import collections
import warnings
import argparse
import sklearn
import pickle
import json
import bz2
import os

# Ignore the Pandas DeprecationWarning
with warnings.catch_warnings():
    warnings.simplefilter(action="ignore", category=DeprecationWarning)
    import pandas

def get_work_dir():
    """Find the path to the project's work directory"""
    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def read_input_file(filename, granularity):
    """Read the input file and save it as one entry per software per run"""

    data = list()

    with bz2.open(filename, "rb") as f:
        for line in f:
            # Load the entry
            entry = json.loads(line)
            for software in entry:
                # Keep the software name (will depend on the granularity type)
                if granularity == "vendor":
                    software_name = software.split("-")[0]
                elif granularity == "major":
                    if "." in software:
                        software_name = software.split(".")[0]
                    else:
                        software_name = software
                elif granularity == "minor":
                    if software.count(".") > 1:
                        software_name = ".".join(software.replace(":latest", "").split(".")[:2])
                    else:
                        software_name = software.replace(":latest", "")
                elif granularity == "build":
                    software_name = software.replace(":latest", "")
                # Go over each query round
                for round in entry[software]:
                    # Store the processed entry
                    round_processed = collections.defaultdict(dict)
                    for testcase in entry[software][round]:
                        # Test results are dictionnaries, which is not deterministic
                        testresult = entry[software][round][testcase]
                        # Instead, we convert them into sorted tuples
                        testresult_sorted = tuple(sorted(list(testresult.items())))
                        # Populate a dictionnary with all the tests for one round
                        round_processed[software_name][testcase] = testresult_sorted
                    # Update the global dictionnary with all the processed round
                    data.append(dict(round_processed))

    return data


def merge_labels(data_raw):
    """Merge labels with identical signatures"""

    # Create a dictionnary with signatures as keys and the list of software as values
    signature_labels = collections.defaultdict(list)
    for entry in data_raw:
        for software in entry:
            signature = tuple(sorted(list(entry[software].items())))
            signature_labels[signature].append(software)

    # Invert the dictionnary to the software:signature form
    # This time, the software may be a concatenation of several labels
    data = list()
    for signature in signature_labels:
        labels_merged = "|".join(tuple(sorted(set(signature_labels[signature]))))
        signature_dictionnary = {i[0]:i[1] for i in signature}
        for _ in range(len(signature_labels[signature])):
            data.append({labels_merged:signature_dictionnary})

    return data


def data_to_df(data_merged):
    """Load the dataset to a Pandas dataframe"""

    # Get all the column names from one of the entries
    column_names_features = [j for i in data_merged[0].values() for j in i]
    column_names_all = ["label"] + column_names_features

    input_data_flat = list()
    for entry in data_merged:
        for software in entry:
            entry_flat = list()
            for column in column_names_all:
                if column == "label":
                    entry_flat.append(software)
                else:
                    entry_flat.append(entry[software][column])
            input_data_flat.append(entry_flat)

    df = pandas.DataFrame(input_data_flat, columns=column_names_all)
    # Do the one hot encoding
    df_one_hot = pandas.get_dummies(data=df, columns=column_names_features)

    return df_one_hot


def create_model(data, testcase_file=None, print_stats = False):
    """Create a Decision tree"""

    # Split the dataset into features and target variables
    X = data.loc[:, data.columns != 'label']
    y = data.label
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.3, random_state=1) 

    # Create Decision Tree classifer object
    clf = sklearn.tree.DecisionTreeClassifier(random_state=1)
    # Train Decision Tree Classifer
    clf = clf.fit(X_train,y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(X_test)

    # Describe the model performance
    model_accuracy = sklearn.metrics.accuracy_score(y_test, y_pred)

    # Analyze the feature importance, i.e. which ones were used to build the tree, and which ones not
    feature_importances = pandas.DataFrame(data=clf.feature_importances_,columns=["importance"],index=X_train.columns)
    # Now we aggregate by the testcase names
    testcases_all = set(i.split("_((")[0] for i in feature_importances.index.to_list())
    testcases_important = set(i.split("_((")[0] for i in feature_importances[feature_importances['importance'] != 0].index.to_list())
    testcases_not_important_unique = testcases_all - testcases_important
    # Also check how many unique versions we got out of all:
    labels_all = set(data["label"].to_list())
    labels_individual = [i for i in labels_all if "|" not in i]
    versions_all = set(j for i in labels_all for j in i.split("|"))

    # Print these metrics
    if print_stats:
        print(f"Accuracy: {model_accuracy}")
        print(f"---")
        print(f"The total number of features: {feature_importances.shape[0]}")
        print(f"  Important features: {feature_importances[feature_importances['importance'] != 0].shape[0]}")
        print(f"  Not important features: {feature_importances[feature_importances['importance'] == 0].shape[0]}")
        print(f"---")
        print(f"The total number of testcases: {len(testcases_all)}")
        print(f"  Important testcases: {len(testcases_important)}")
        print(f"  Not important testcases: {len(testcases_not_important_unique)}")
        print(f"---")
        print(f"All versions: {len(versions_all)}")
        print(f"  Individual versions: {len(labels_individual)}")

    # Write testcase names that were used to build trees
    if testcase_file:
        with open(testcase_file, "w") as f:
            for testcase in sorted(testcases_important):
                f.write(f"{testcase}\n")

    # Return the model
    return clf
