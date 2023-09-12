import collections
import testcases
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
    with open(f"{work_dir}/software/versions_major.txt", "r") as f:
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


def run_containers(images_list, network_custom):
    """Run the containers in our custom network"""

    # Store the container objects
    containers = list()
    for image in images_list:
        logging.info("Starting the %s container", image)
        container_new = client.containers.run(image=image, network = network_custom, detach=True, tty=True)
        containers.append(container_new)

    return containers


def stop_and_remove_containers(containers_list):
    """Stop and remove all our containers running DNS software"""

    # Stop and remove each container one by one
    for container in containers_list:
        logging.info("Stopping the %s container", container.image)
        container.stop()
        logging.info("Removing the %s container", container.image)
        container.remove()


def get_targets(containers_list, network_custom):
    """Generate IP addresses to scan together with software names"""

    # Extract image name and IP addresses of each running container
    # Store as a list of tuples
    targets = list()
    for container in containers_list:
        container.reload()
        container_ip = container.attrs["NetworkSettings"]["Networks"][network_custom]["IPAddress"]
        container_image = container.attrs["Config"]["Image"]
        targets.append((container_image, container_ip))

    # Additionally, get IP addresses of machines running Windows Server
    targets.append(("windows-server:2022",os.getenv("WS_IP_2022")))
    targets.append(("windows-server:2019",os.getenv("WS_IP_2019")))
    targets.append(("windows-server:2016",os.getenv("WS_IP_2016")))

    return targets


if __name__ == '__main__':

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
    containers = run_containers(images_list=images, network_custom=fpdns_network.name)

    # Generate targets to scan (software, IP)
    # This includes containers + Windows machines
    targets = get_targets(containers_list=containers, network_custom=fpdns_network.name)

    # Let all the programs inside containers start
    time.sleep(30)
    
    # Execute queries and store results for each software vendor inside the results dictionnary
    results = collections.defaultdict(dict)
    for target_to_scan in targets:
        results[target_to_scan[0]]["test_1"] = testcases.test_1(target=target_to_scan[1], domain=os.getenv("DOMAIN"))
        results[target_to_scan[0]]["test_6"] = testcases.test_6(target=target_to_scan[1])
        results[target_to_scan[0]]["test_7"] = testcases.test_7(target=target_to_scan[1], domain=os.getenv("DOMAIN"))

    # Save the results
    with open(f"{work_dir}/signatures/signatures.json", "w") as f: 
        json.dump(results,f)

    # Stop and remove containers
    stop_and_remove_containers(containers_list=containers)

    # Remove the Docker network
    fpdns_network.remove()
