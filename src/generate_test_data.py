# Copyright 2026 Yevheniya Nosyk
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

from pathlib import Path
import logging
import docker

def get_work_dir():
    """Find the path to the project's work directory"""
    # The location of this file
    path = Path(__file__).resolve()
    # Go up intil the git root found
    for parent in path.parents:
        if (parent / ".git").exists():
            return parent

def get_resolver_images(dir,client):
    """Build resolver images or get existing ones"""

    # The list of resolver images
    images = list()
    # Get the list of images that exist already on the system
    images_local = [image.tags[0] for image in client.images.list() if image.tags]

    # Read the list of images to build
    with open(dir / "software" / "software.txt", "r") as f:
        for software in f:
            # Extract the vendor and version information
            vendor, version_major, version_minor = software.strip().split("/")
            logging.info("Processing %s-%s", vendor, version_minor)
            # Construct the image tag
            image_tag = f"dnssoftver-{vendor}-{version_minor}:latest"
            # Build if not already done
            if image_tag not in images_local:
                logging.info("Building %s-%s", vendor, version_minor)
                # Path to the Dockerfile
                dockerfile_dir = dir / "software" / vendor / version_major / version_minor
                # Ensure Dockerfile exists
                if not (dockerfile_dir / "Dockerfile").exists():
                    logging.error("Could not find a Dockerfile for %s-%s", vendor, version_minor)
                    continue
                # Ensure to remove the intermediate containers and dangling images while building
                docker_client.images.build(path=str(dockerfile_dir), tag=image_tag, rm=True)
                client.images.prune(filters={'dangling': True})
                logging.info("Built %s-%s", vendor, version_minor)
            # Image processed
            images.append(image_tag)
            logging.info("Processed %s-%s", vendor, version_minor)

    # Return the list of resolver images
    return images


if __name__ == "__main__":

    # Get the work directory of this project
    work_dir = get_work_dir()

    # Configure logging
    logging.basicConfig(
        filename=str(work_dir / "log.log"),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Create a Docker client
    docker_client = docker.from_env()

    # Build resolver images
    resolver_images = get_resolver_images(dir=work_dir,client=docker_client)
