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
import argparse
import sklearn
import pandas
import json
import os

def get_work_dir():
    """Find the path to the project's work directory"""
    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def read_input_file(filename, granularity):
    """Read the input file and save it as one entry per software per run"""

    data = list()

    with open(filename, "r") as f:
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


def create_model(data,tree_file, performance_file):
    """Create a Decision tree"""

    # Split the dataset into features and target variables
    X = data.loc[:, data.columns != 'label']
    y = data.label
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.2, random_state=1) 

    # Create Decision Tree classifer object
    clf = sklearn.tree.DecisionTreeClassifier(random_state=1)
    # Train Decision Tree Classifer
    clf = clf.fit(X_train,y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(X_test)

    # Print the decision tree, but make feature names more human-readable
    features_one_hot = data.columns.difference(["label"], sort=False).tolist()
    # Here we remove all the brackets and join by pipes
    features_short = list()
    # In this list we only keep testcase names
    features_testcases = list()
    for i in features_one_hot:
        features_short.append(i.replace("'","").replace("), (","_").replace(", ","-").replace("_((","---").replace("))","").replace("),)",""))
        features_testcases.append(i[:i.index("(")][:-1])

    # Print the tree in a text form with feature names in a short format
    text_representation = sklearn.tree.export_text(clf,feature_names=features_short, max_depth=len(features_one_hot))

    # Also save to the text file
    with open(tree_file, "w") as f:
        f.write(text_representation)

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

    # Write these metrics to a file
    with open(performance_file, "w") as f:
        f.write(f"Accuracy: {model_accuracy}\n")
        f.write(f"---\n")
        f.write(f"The total number of features: {feature_importances.shape[0]}\n")
        f.write(f"  Important features: {feature_importances[feature_importances['importance'] != 0].shape[0]}\n")
        f.write(f"  Not important features: {feature_importances[feature_importances['importance'] == 0].shape[0]}\n")
        f.write(f"---\n")
        f.write(f"The total number of testcases: {len(testcases_all)}\n")
        f.write(f"  Important testcases: {len(testcases_important)}\n")
        f.write(f"  Not important testcases: {len(testcases_not_important_unique)}\n")
        f.write(f"---\n")
        f.write(f"All versions: {len(versions_all)}\n")
        f.write(f"  Individual versions: {len(labels_individual)}\n")


if __name__ == '__main__':

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--granularity', required=True, choices=["vendor", "major", "minor", "build"], type=str, help="The fingerprinting granularity")
    args = parser.parse_args()

    # Get the working directory
    work_dir = get_work_dir()

    # Read the input file with test results and save it as one entry per software per run
    input_data = read_input_file(filename=f"{work_dir}/signatures/signatures_all.json", granularity=args.granularity)

    # Some signatures can correspond to multiple labels
    # However, in this case the decision tree will not work correctly
    # So, we need to merge those labels
    input_data_merged_labels = merge_labels(data_raw=input_data)

    # Load the processed input dataset to a DataFrame to be then passed to the classifier
    input_data_df = data_to_df(data_merged=input_data_merged_labels)

    # Create the model
    create_model(data=input_data_df, tree_file=f"{work_dir}/trees/tree_{args.granularity}.txt", performance_file=f"{work_dir}/models/performance_{args.granularity}.txt")
