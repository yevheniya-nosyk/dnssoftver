import logging
import docker
import os 

def get_work_dir():
    """Find the path to the project's work directory"""
    return os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]


def get_images(docker_client, work_dir_path):
    """Build DNS software images from Dockerfiles or pull from DockerHub"""

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
                    docker_client.images.build(path=f"{work_dir_path}/software/{path_to_dockerfile}", tag=image_tag, rm=True)
                # If the path to the Dockerfile was not found (the case of some Knot Resolver versions), 
                # we need to pull the official image provided by CZ.NIC 
                except TypeError:
                    if vendor == "knot-resolver":
                        docker_client.images.pull(repository="cznic/knot-resolver", tag=f"v{version}")
                logging.info("Processed %s-%s", vendor, version)
            else:
                logging.info("Skipping %s-%s", vendor, version)


if __name__ == '__main__':

    # Get the working directory
    work_dir = get_work_dir()

    # Configure logging
    logging.basicConfig(filename=f"{work_dir}/logging.log", level=logging.INFO, format='%(asctime)s %(name)s %(processName)s %(threadName)s %(levelname)s:%(message)s')

    # Instantiate the Docker client
    client = docker.from_env()

    # Build Docker images
    get_images(docker_client=client, work_dir_path=work_dir)
