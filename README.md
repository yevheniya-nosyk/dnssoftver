# fpdns

A tool to fingerprint DNS resolver software.

## Software

Below is the list of the supported DNS software and versions:

| Software | Role | Supported Versions | Installation type | Notes |
|-|-|-|-|-|
| [BIND9](https://www.isc.org/bind/) | Recursive | `9.12.0`, `9.13.0`, `9.14.0`, `9.15.0`, `9.16.0`, `9.17.0`, `9.18.0`, `9.19.0` | Docker | <ul><li>[Source code since version 9.0.0](https://downloads.isc.org/isc/bind9/)</li><li>[BIND 9 Significant Features Matrix](https://kb.isc.org/docs/aa-01310)</li><li>[CHANGELOG](https://gitlab.isc.org/isc-projects/bind9/-/blob/main/CHANGES)</li><li>[How to build and run named](https://kb.isc.org/docs/aa-00768)</li></ul> |
| [Windows Server](https://www.microsoft.com/en-us/windows-server) | Recursive | `2016 Standard`, `2019 Standard`, `2022 Standard` | VPS | | 

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

### Environment variables

Create a `.env` file in the root of this repository and gradually add variables there. The file is not tracked by git.

## Installation

### Windows Server

We rent 3 virtual private servers with the following operating systems: Windows Server 2022, Windows Server 2019, Windows Server 2016. Add the corresponding IP addresses to the `.env` file under `WS_IP_2022`, `WS_IP_2019`, `WS_IP_2016`.

To configure, go to: Server Manager -> Dashboard -> Add roles and features -> Role-based or feature-based installation -> Select a server from the server pool -> DNS server -> Install.

Check that it works by sending a simple recursive query to the server's IP address:

```bash
$ dig @<server_ip> google.com
```

### Other software

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
