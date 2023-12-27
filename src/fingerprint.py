import multiprocessing
import collections
import testcases
import argparse
import logging
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

    # Additionally, get IP addresses of machines running Windows Server
    targets.append(("windows-server:2022",os.getenv("WS_IP_2022")))
    targets.append(("windows-server:2019",os.getenv("WS_IP_2019")))
    targets.append(("windows-server:2016",os.getenv("WS_IP_2016")))

    return targets


def fingerprint_resolver(software,ip_address):
    """Issue queries to fingerprint a resolver"""

    fingerprint = collections.defaultdict(dict)
    fingerprint[software]["test_baseline"] = testcases.test_baseline(target=ip_address, domain=f"baseline.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_norec"] = testcases.test_norec(target=ip_address, domain=f"norec.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_iquery"] = testcases.test_iquery(target=ip_address, domain=f"iquery.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_chaos_rd"] = testcases.test_chaos_rd(target=ip_address, domain=f"chaos.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_is_response"] = testcases.test_is_response(target=ip_address, domain=f"response.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_tc"] = testcases.test_tc(target=ip_address, domain=f"tc.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_zero_ttl"] = testcases.test_zero_ttl(target=ip_address, domain=f"zero-ttl.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_edns0"] = testcases.test_edns0(target=ip_address, domain=f"edns0.{os.getenv('DOMAIN')}")
    fingerprint[software]["test_home_arpa"] = testcases.test_local_zone(target=ip_address, domain="home.arpa")
    fingerprint[software]["test_31_172"] = testcases.test_local_zone(target=ip_address, domain="31.172.in-addr.arpa")
   
    return fingerprint

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
    results = list()

    # Repeat all the tests 5 times
    repeats = 5
    while repeats:

        # Start containers and store container IDs
        containers = list()
        for image in images:
            containers.append(run_container(image))

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
        
        # Execute queries and store results for each software vendor inside the results list
        with multiprocessing.Pool(15) as p:
            results_local = p.starmap(fingerprint_resolver,targets)
        results.extend(results_local)

        # Remove containers
        for container in containers:
            remove_container(container)

        repeats -= 1

    # Save the results
    with open(f"{work_dir}/signatures/signatures_{args.versions}.json", "w") as f: 
        for result in results:
            f.write(f"{json.dumps(result)}\n")

    # Remove the Docker network
    fpdns_network.remove()
