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

import multiprocessing
import fingerprint
import collections
import testcases
import ipaddress
import itertools
import argparse
import warnings
import logging
import pickle
import json
import os

# Ignore the Pandas DeprecationWarning
with warnings.catch_warnings():
    warnings.simplefilter(action="ignore", category=DeprecationWarning)
    import pandas

def get_work_dir():
    """Find the path to the project's work directory"""

    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def load_model(model_file):
    """Load the pickled model"""

    with open(model_file, 'rb') as f:
        model = pickle.load(f)

    return model


def get_testcases(filename):
    """Return a list of testcase names"""

    data = list()
    with open(filename,"r") as f:
        for testcase in f:
            data.append(testcase.strip())
    return data
    

def get_model_data(data_input,model):
    """Prepare the data for the decision tree"""

    # Process the data so that signatures become tuples
    data_processed = list()

    for ip in data_input:
        # Store the processed ip entry
        entry_processed = collections.defaultdict(dict)
        for testcase in data_input[ip]:
            # Test results are dictionnaries, which is not deterministic
            testresult = data_input[ip][testcase]
            # Instead, we convert them into sorted tuples
            testresult_sorted = tuple(sorted(list(testresult.items())))
            # Populate a dictionnary with all the tests for this entry
            entry_processed[ip][testcase] = testresult_sorted
        data_processed.append(dict(entry_processed))

    # Get all the column names from one of the entries
    column_names_features = [j for i in data_processed[0].values() for j in i]
    column_names_all = ["ip"] + column_names_features
    # Make the processed data flat
    data_processed_flat = list()
    for entry in data_processed:
        for ip in entry:
            entry_flat = list()
            for column in column_names_all:
                if column == "ip":
                    entry_flat.append(ip)
                else:
                    entry_flat.append(entry[ip][column])
            data_processed_flat.append(entry_flat)

    # Create a DataFrame
    df = pandas.DataFrame(data_processed_flat, columns=column_names_all)       
    # Do the one hot encoding
    df_one_hot = pandas.get_dummies(data=df, columns=column_names_features)

    # We need to ensure that the dataset includes all the features used at the training stage, 
    # even if the feature is equal to 0
    for feature in model.feature_names_in_:
        if feature not in df_one_hot.columns:
            df_one_hot[feature] = False

    return df_one_hot


def append_result(filename,data):
    """Append the chunk result to the output file"""

    with open(filename,"a") as f:
        for entry in data:
            result = {"ip": entry[0], "versions": entry[1].split("|")}
            f.write(f"{json.dumps(result)}\n")


if __name__ == '__main__':

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', required=True, type=str, help="The input file with one IP address per line")
    parser.add_argument('-o', '--output_file', required=True, type=str, help="The output file with fingerprinting results")
    parser.add_argument('-t', '--threads', required=False, default=100, type=int, help="The number of threads, defaults to 100")
    parser.add_argument('-g', '--granularity', required=True, choices=["vendor", "major", "minor", "build"], type=str, help="The fingerprinting granularity")
    args = parser.parse_args()

    # Ignore some of the Pandas warnings
    warnings.simplefilter(action="ignore", category=pandas.errors.PerformanceWarning)

    # Get the working directory
    work_dir = get_work_dir()

    # Configure logging
    logging.basicConfig(filename=f"{work_dir}/dnssoftver.log", level=logging.WARNING, format='%(asctime)s %(name)s %(processName)s %(threadName)s %(levelname)s:%(message)s')

    # Depending on the granularity chosen, load the corresponding model pickle
    decision_tree = load_model(model_file=f"{work_dir}/data/models/model_{args.granularity}.pkl")

    # Get the names of the testcases that were used to build the tree
    testcase_names = get_testcases(filename=f"{work_dir}/data/queries/queries_{args.granularity}.txt")

    # We process the input file in chunks
    with open(args.input_file, "r") as f:
        while True:
            chunk = list(itertools.islice(f, int(args.threads/3)))
            if chunk:
                # Ensure that all the entries in the current chunk are valid IP addresses
                ips_to_scan = list()
                for ip in chunk:
                    # Remove leading and trailing whitespaces from each input line
                    ip = ip.strip()
                    # Check that the string is a valid IPv4 or IPv6 address
                    try:
                        ipaddress.ip_address(ip)
                        ips_to_scan.append(ip)
                    except ValueError as e:
                        logging.warning(e)
                        continue
                # Process the chunk of IPs if not empty
                if ips_to_scan:
                    # The number of threads is the minimum of the chunk size and the value passed to the program
                    threads = min(args.threads,len(ips_to_scan)*3)
                    # To reuse functions from the fingerprinting stage, we need to create to-scan
                    # tuples with software names (unknown in this case) and ip addresses
                    # Generate all the queries possible
                    queries_all = fingerprint.generate_queries(query_targets=ips_to_scan,is_scanner=True) 
                    # However, we only need to issue testcases that were used to generate the decision tree
                    queries_important = [i for i in queries_all if i["query_name"] in testcase_names]
                    # Run the test cases
                    with multiprocessing.pool.ThreadPool(threads) as p:
                        results= p.map(testcases.generate_dns_query, queries_important)
                    # Group the results obtained above by IP addresses
                    results_chunk = collections.defaultdict(dict)
                    for result in results:
                        results_chunk[result["ip"]][result["query_name"]] = result["signature"]
                    # Prepare the query results to be consumed by a model
                    df_results_chunk = get_model_data(data_input=results_chunk,model=decision_tree)
                    # Classify
                    df_results_chunk_test =  df_results_chunk.loc[:, df_results_chunk.columns != 'ip']
                    # Columns in train and test datasets must be in the same order
                    df_results_chunk_test = df_results_chunk_test[decision_tree.feature_names_in_]
                    df_results_chunk_pred =  decision_tree.predict(df_results_chunk_test)
                    # Save the chunk result as tuples and write to the output file
                    chunk_predicted = zip(df_results_chunk["ip"].tolist(),df_results_chunk_pred.tolist())
                    append_result(filename=args.output_file, data=chunk_predicted)
            else:
                break
