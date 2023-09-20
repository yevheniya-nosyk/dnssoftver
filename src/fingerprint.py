import multiprocessing
import collections
import testcases
import argparse
import logging
import docker
import dotenv
import time
import json
import os 

def get_work_dir():
    """Find the path to the project's work directory"""
    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def get_images(docker_client, work_dir_path):
    """Build DNS software images from Dockerfiles or pull from DockerHub"""

    images = list()

    # Get the list of images that exist already on the system
    images_local = [image.tags[0] for image in docker_client.images.list() if image.tags]

    # Read the list of software
    with open(f"{work_dir}/software/versions_{args.versions}.txt", "r") as f:
        for software in f:
            # Extract vendor and version information
            vendor, _ , version = software.strip().split("/")
            logging.info("Processing %s-%s", vendor, version)
            # We have Dockerfiles for non-Microsoft software
            if vendor != "microsoft":
                # Store the path to Dockerfile
                path_to_dockerfile = software.strip()
                # Store the image tag
                image_tag = f"{vendor}-{version}"
                # Try to build the image locally
                try:
                    if image_tag not in images_local:
                        docker_client.images.build(path=f"{work_dir_path}/software/{path_to_dockerfile}", tag=image_tag, rm=True)
                    images.append(f"{image_tag}:latest")
                # If the path to the Dockerfile was not found (the case of some Knot Resolver versions), 
                # we need to pull the official image provided by CZ.NIC 
                except TypeError:
                    if vendor == "knot-resolver":
                        image_tag = f"cznic/knot-resolver:v{version}"
                        if image_tag not in images_local:
                            docker_client.images.pull(repository="cznic/knot-resolver", tag=f"v{version}")
                        images.append(image_tag)
                logging.info("Processed %s-%s", vendor, version)
            else:
                logging.info("Skipping %s-%s", vendor, version)

    return images


def run_container(image_to_build):
    """Run the container in our custom network"""

    logging.info("Starting the %s container", image_to_build)
    container = client.containers.run(image=str(image_to_build), network = "fpdns", detach=True, tty=True)
    return container.id


def stop_and_remove_container(container_id):
    """Stop and remove all our containers running DNS software"""

    # Recreate a container object, then stop and remove it
    container = client.containers.get(container_id=container_id)
    logging.info("Stopping the %s container", container.image)
    container.stop()
    logging.info("Removing the %s container", container.image)
    container.remove()


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


def fingerprint_resolver(target):
    """Issue queries to fingerprint a resolver"""

    fingerprint = collections.defaultdict(dict)
    fingerprint[target[0]]["test_baseline"] = testcases.test_baseline(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_baseline_norec"] = testcases.test_baseline_norec(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_nx_subdomain"] = testcases.test_nx_subdomain(target=target[1], domain={os.getenv('DOMAIN')})
    fingerprint[target[0]]["test_iquery"] = testcases.test_iquery(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_chaos_rd"] = testcases.test_chaos_rd(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_is_response"] = testcases.test_is_response(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_tc"] = testcases.test_tc(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_zero_ttl"] = testcases.test_zero_ttl(target=target[1], domain=f"zero-ttl.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_edns0"] = testcases.test_edns0(target=target[1], domain=f"example.{os.getenv('DOMAIN')}")
    fingerprint[target[0]]["test_home_arpa"] = testcases.test_local_zone(target=target[1], domain="home.arpa")
   
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

    # Build Docker images
    images = get_images(docker_client=client, work_dir_path=work_dir)

    # Create a Docker network for this project
    fpdns_network = client.networks.create(name="fpdns")

    # Run containers
    with multiprocessing.Pool(15) as p:
        containers = p.map(run_container,images)

    # Generate targets to scan (software, IP)
    # This includes containers + Windows machines
    targets = get_targets(containers_list=containers, network_custom=fpdns_network.name)

    # Let all the programs inside containers start
    time.sleep(30)
    
    # Execute queries and store results for each software vendor inside the results дшіе
    results = list()
    with multiprocessing.Pool(15) as p:
       results = p.map(fingerprint_resolver,targets)

    # Save the results
    with open(f"{work_dir}/signatures/signatures_{args.versions}.json", "w") as f: 
        for result in results:
            f.write(f"{json.dumps(result)}\n")

    # Stop and remove containers
    with multiprocessing.Pool(15) as p:
        p.map(stop_and_remove_container,containers)

    # Remove the Docker network
    fpdns_network.remove()
