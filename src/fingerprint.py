import multiprocessing.pool
import multiprocessing
import collections
import testcases
import itertools
import argparse
import logging
import random
import docker
import dotenv
import time
import json
import csv
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
    with open(f"{work_dir}/software/versions_{args.versions}.txt", "r") as f:
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


def generate_queries(query_targets):
    """Generate all the possible query combinations"""

    # Will store the result
    queries = list()

    for target in query_targets:
        for query_combo in (dict(zip(testcases.query_options.keys(), values)) for values in itertools.product(*testcases.query_options.values())):
            # Assign this query a name
            query_name = "_".join([query_combo[i] for i in query_combo if query_combo[i]]).replace(f".{os.getenv('DOMAIN')}", "")
            # Create a dictionnary with all the query options that will be passed to testcases.generate_dns_query()
            query = {
                "query_name": query_name,
                "software": target[0],
                "ip": target[1],
                "query_options": query_combo
            }
            # Append to the list of queries
            queries.append(query)
    
    # Shuffle the list so that one resolver does not get all the queries at once
    random.shuffle(queries)

    return queries

if __name__ == '__main__':

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--versions', required=True, choices=["minor", "all"], type=str)
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

    # Repeat all the tests 5 times
    repeats = 5
    while repeats:

        # Process 75 images at a time
        batch_size = 75
        for i in range(0,len(images),batch_size):

            # Local batch of 50 images that we will create containers from
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

            # Generate all the queries to be executed
            queries_all = generate_queries(query_targets=targets)    

            # Execute queries and store results inside the results list
            with multiprocessing.pool.ThreadPool(batch_size*10) as p:
                results_local = p.map(testcases.generate_dns_query, queries_all)

            # Write the local result to the main results dictionnary
            for result in results_local:
                results[result["software"]][f"round_{repeats}"].update({result["query_name"]: result["signature"]})

            # Remove containers
            with multiprocessing.Pool(15) as p:
                p.map(remove_container,containers)

        repeats -= 1

    # Save the results
    with open(f"{work_dir}/signatures/signatures_{args.versions}.json", "w") as f: 
        for result in results:
            f.write(f"{json.dumps({result:results[result]})}\n")

    # Remove the Docker network
    fpdns_network.remove()
