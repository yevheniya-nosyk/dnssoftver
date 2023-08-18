# fpdns

A tool to fingerprint DNS resolver software.

## Software

Below is the list of the supported DNS software and versions:

| Software | Role | Supported Versions | Installation type | Notes |
|-|-|-|-|-|
| [BIND9](https://www.isc.org/bind/) | Recursive | `9.18.0`, `9.19.0` | Docker | <ul><li>[Source code since version 9.0.0](https://downloads.isc.org/isc/bind9/)</li> <li>[CHANGELOG](https://gitlab.isc.org/isc-projects/bind9/-/blob/main/CHANGES)</li><li>[How to build and run named](https://kb.isc.org/docs/aa-00768)</li></ul> |

## Prerequisites 

### Docker

Depending on your system, follow the [official guidelines](https://docs.docker.com/engine/install/) on Docker installation.

To avoid running Docker with `sudo`, add your user to the `docker` group:

```bash
sudo usermod -a -G docker <username>
```

Some of the useful commands:

```bash
# List images
$ docker images
# List running containers
$ docker ps
# List all containers
$ docker ps -a
```

## Installation

### Docker

Directory `software/<vendor>/<version>/` contains `Dockerfile`s  used to install and run most of the DNS software.

To test one software instance:

```bash
# Build the image
$ docker build -t <your_image_name> <path_to_dockerfile_dir>
# Run the container
$ docker run -d -p 127.0.0.1:5353:53/tcp -p 127.0.0.1:5353:53/udp -t <your_image_name>
# You can now query the container
$ dig @127.0.0.1 -p 5353 google.com
# Stop and delete the container
$ docker stop <container_id> && docker rm <container_id>
# Delete the image
$ docker rmi <your_image_name>
```
