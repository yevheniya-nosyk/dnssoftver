# Build from stratch

This project was built on Debian GNU/Linux 12 (bookworm) using Python 3.11.2.

## Installation

### Virtual environment

```bash
$ python3 -m virtualenv -p python3.11 .venv
$ source .venv/bin/activate
$ pip3 install -r requirements.txt
```

### Docker

Depending on your system, follow the [official guidelines](https://docs.docker.com/engine/install/) on Docker installation.

To avoid running Docker with `sudo`, add your user to the `docker` group:

```bash
$ sudo usermod -a -G docker <username>
```

You may want to change the Docker root directory, because all the images will take up some space. Here is how to do it:

```bash
# Stop Docker
$ sudo systemctl stop docker
# Create your new directory
$ mkdir /home/docker
# Copy
$ sudo rsync -avxP /var/lib/docker/ /home/docker
# Create/modify this file
$ sudo vim /etc/docker/daemon.json
# Add the following:
#
# {
#     "data-root": "/home/docker"
# }
#
# Reload everything
$ sudo systemctl daemon-reload
$ sudo systemctl start docker
# Check the new dir
$ docker info | grep "Docker Root Dir"
```

Some useful commands:

```bash
# List images
$ docker images
# List running containers
$ docker ps
# List all containers
$ docker ps -a
# Remove all images
$ docker rmi $(docker images -q)
# Kill all containers
$ docker rm -f $(docker ps -aq)
```

How to build/test a piece of software:

```bash
# Build an image
$ docker build -t <image_name> <path_to_dockerfile>
# Start a container
$ docker run -d -p 127.0.0.1:5353:53/udp -t <image_name>
# Safe choice
$ dig @127.0.0.1 -p 5353 A google.com +short
# May not be available in all the software
$ dig @127.0.0.1 -p 5353 CH TXT version.bind +short
# Kill the container
$ docker rm -f <container_id>
```

## Run

First, we need to generate some queries/responses that will later be used to create signatures. The script below builds all the Docker containers found in `software/software.txt`:

```bash
$ python3 src/generate_test_data.py
```
