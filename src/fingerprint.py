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

import multiprocessing.pool
import multiprocessing
import collections
import testcases
import itertools
import argparse
import logging
import docker
import dotenv
import scan
import time
import json
import csv
import bz2
import os 

def get_work_dir():
    """Find the path to the project's work directory"""
    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def get_images(docker_client, work_dir_path):
    """Build DNS software images from Dockerfiles or pull from DockerHub"""

    # Store all the resolver images
    images = list()

    # Get the list of images that exist already on the system so that we do not build them again
    images_local = [image.tags[0] for image in docker_client.images.list() if image.tags]

    # Read the list of software
    with open(f"{work_dir_path}/software/versions_all.txt", "r") as f:
        software_all = list(csv.reader(f))
        for software in software_all:
            # Extract vendor and version information
            vendor, _ , version = software[0].strip().split("/")
            logging.info("Processing %s-%s", vendor, version)
            # There are three types of software installations:
            # - local Dockerfile
            # - remote image repository
            # - virtual private server
            installation_type = software[1]
            if installation_type != "vps":
                # If our software is not a VPS, then we will deal with Docker images
                if installation_type == "dockerfile":
                    # Store the path to Dockerfile:
                    path_to_dockerfile = software[0]
                    # Store the image tag
                    image_tag = f"{vendor}-{version}"
                    # Ensure the image is not already built
                    if image_tag not in images_local:
                        docker_client.images.build(path=f"{work_dir_path}/software/{path_to_dockerfile}", tag=image_tag, rm=True)
                elif installation_type == "remote":
                    # Store the remote repository
                    repository_remote = software[2]
                    # Store the remote and local image tags
                    image_tag = f"{vendor}-{version}"
                    image_tag_remote = f"{repository_remote}:v{version}"
                    # Ensure the image is not already built
                    if image_tag not in images_local:
                        # Pull the image and create a new tag that follows our local naming convention
                        docker_client.images.pull(repository=repository_remote, tag=f"v{version}").tag(repository=image_tag)
                        # Remove the original image
                        docker_client.images.remove(image=image_tag_remote)
                # Save the image we have just processed
                images.append(f"{image_tag}:latest")
                logging.info("Processed %s-%s", vendor, version)
            else:
                logging.info("Skipping %s-%s because it is a VPS", vendor, version)

    return images


def run_container(image_to_build):
    """Run the container in our custom network"""

    logging.info("Starting the %s container", image_to_build)
    container = client.containers.run(image=str(image_to_build), network = "fpdns", detach=True, tty=True)
    return container.id


def remove_container(container_id):
    """Remove all our containers running DNS software"""

    # Recreate a container object, then remove it
    container = client.containers.get(container_id=container_id)
    logging.info("Removing the %s container", container.image)
    container.remove(force=True)


def get_targets(containers_list, network_custom):
    """Generate IP addresses to scan together with software names"""

    # Extract image name and IP addresses of each running container
    # Store as a list of tuples
    targets = list()
    for container_id in containers_list:
        container = client.containers.get(container_id=container_id)
        container.reload()
        container_ip = container.attrs["NetworkSettings"]["Networks"][network_custom]["IPAddress"]
        container_image = container.attrs["Config"]["Image"]
        targets.append((container_image, container_ip))

    return targets

def execute_queries_all(software_to_fingerprint,ip_to_fingerprint):
    """Generate all the query combinations and issue them"""

    results_per_software = list()
    for query_combo in (dict(zip(testcases.query_options.keys(), values)) for values in itertools.product(*testcases.query_options.values())):
        # Assign this query a name
        query_name = "_".join([query_combo[i] for i in query_combo if query_combo[i]]).replace(".dnssoftver.com", "")
        query = {
                "query_name": query_name,
                "software": software_to_fingerprint,
                "ip": ip_to_fingerprint,
                "query_options": query_combo
            }
        query_response = testcases.generate_dns_query(q_options=query)
        results_per_software.append(query_response)
    
    return results_per_software

def execute_queries_important(software_to_fingerprint,ip_to_fingerprint):
    """Generate all the query combinations and only execute important ones"""

    results_per_software = list()
    for query_combo in (dict(zip(testcases.query_options.keys(), values)) for values in itertools.product(*testcases.query_options.values())):
        # Assign this query a name
        query_name = "_".join([query_combo[i] for i in query_combo if query_combo[i]]).replace(".dnssoftver.com", "")
        if query_name in testcases_important:
            query = {
                    "query_name": query_name,
                    "software": software_to_fingerprint,
                    "ip": ip_to_fingerprint,
                    "query_options": query_combo
                }
            query_response = testcases.generate_dns_query(q_options=query)
            results_per_software.append(query_response)
    
    return results_per_software


if __name__ == '__main__':

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repeats', required=True, default=10, type=int)
    parser.add_argument('-g', '--granularity', required=False, choices=["vendor", "major", "minor", "build"], type=str, help="The fingerprinting granularity")
    args = parser.parse_args()

    # Get the working directory
    work_dir = get_work_dir()

    # Load the .env file
    dotenv.load_dotenv()

    # Configure logging
    logging.basicConfig(filename=f"{work_dir}/logging.log", level=logging.INFO, format='%(asctime)s %(name)s %(processName)s %(threadName)s %(levelname)s:%(message)s')

    # Instantiate the Docker client
    client = docker.from_env()

    # Build Docker images if do not exist yet
    images = get_images(docker_client=client, work_dir_path=work_dir)

    # Create a Docker network for this project
    fpdns_network = client.networks.create(name="fpdns")

    # Store testing results in the list
    results = collections.defaultdict(lambda: collections.defaultdict(dict))

    # Repeat all the tests the number of repeats
    repeats = args.repeats
    while repeats:

        # Process 400 images at a time
        batch_size = 400
        for i in range(0,len(images),batch_size):

            # Local batch of images that we will create containers from
            images_local = images[i:i+batch_size]

            # Start containers and store container IDs
            with multiprocessing.Pool(15) as p:
                containers = p.map(run_container,images_local)

            # Wait until all the containers are running
            for container_id in containers:
                # Recreate the container object
                container = client.containers.get(container_id=container_id)
                # Set the condition
                status = container.status
                while status != "running":
                    time.sleep(5)
                    container.reload()
                    status = container.status

            # Generate targets to scan (software, IP)
            # This includes containers + Windows machines
            targets = get_targets(containers_list=containers, network_custom=fpdns_network.name)

            # Additionally, get IP addresses of machines running Windows Server, but only once
            if ("windows-server:2022" not in results) or (f"round_{repeats}" not in results["windows-server:2022"]):
                targets.append(("windows-server:2022",os.getenv("WS_IP_2022")))
                targets.append(("windows-server:2019",os.getenv("WS_IP_2019")))
                targets.append(("windows-server:2016",os.getenv("WS_IP_2016")))

            # Execute queries and store results inside the results list
            if args.granularity:
                testcases_important = scan.get_testcases(filename=f"{work_dir}/data/queries/queries_{args.granularity}.txt")
                with multiprocessing.pool.ThreadPool(len(targets)) as p:
                    results_batch = p.starmap(execute_queries_important, targets)
            else:
                with multiprocessing.pool.ThreadPool(len(targets)) as p:
                    results_batch = p.starmap(execute_queries_all, targets)

            # Write the batch result to the main results dictionnary
            for software in results_batch:
                for result in software:
                    results[result["software"]][f"round_{repeats}"].update({result["query_name"]: result["signature"]})

            # Remove containers
            with multiprocessing.Pool(15) as p:
                p.map(remove_container,containers)

        # Generate the signature filename
        if args.granularity:
            signatures_file = f"{work_dir}/signatures/signatures_{args.granularity}.json.bz2"
        else:
            signatures_file = f"{work_dir}/signatures/signatures_all.json.bz2"
        # Save the results after every round
        with bz2.open(signatures_file, "wb") as f: 
            for result in results:
                f.write(f"{json.dumps({result:results[result]})}\n".encode())

        repeats -= 1

    # Remove the Docker network
    fpdns_network.remove()
