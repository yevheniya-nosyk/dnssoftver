# fpdns

A tool to fingerprint DNS resolver software.

## Software

Below is the list of the supported DNS software and versions:

| Software | Role | Supported Versions | Installation type | Notes |
|-|-|-|-|-|
| [BIND9](https://www.isc.org/bind/) | Recursive | `9.10.0-9.10.8rc2`, `9.11.0-9.11.37`, `9.12.0-9.12.4rc1`, `9.13.0-9.13.7`, `9.14.0-9.14.12`, `9.15.0-9.15.8`, `9.16.0-9.16.43`, `9.17.0-9.17.22`, `9.18.0-9.18.18`, `9.19.0-9.19.16` | Docker | <ul><li>[Source code since version 9.0.0](https://downloads.isc.org/isc/bind9/)</li><li>[BIND 9 Significant Features Matrix](https://kb.isc.org/docs/aa-01310)</li><li>[CHANGELOG](https://gitlab.isc.org/isc-projects/bind9/-/blob/main/CHANGES)</li><li>[How to build and run named](https://kb.isc.org/docs/aa-00768)</li></ul> |
| [Unbound](https://www.nlnetlabs.nl/projects/unbound/about/) | Recursive | `1.5.0-1.5.10rc1`, `1.6.0-1.6.8`, `1.7.0-1.7.3rc2`, `1.8.0-1.8.3`, `1.9.0-1.9.6rc1`, `1.10.0-1.10.1`, `1.11.0-1.11.0rc1`, `1.12.0-1.12.0rc1`, `1.13.0-1.13.2rc1`, `1.14.0-1.14.0rc1`, `1.15.0-1.15.0rc1`, `1.16.0-1.16.3`, `1.17.0-1.17.1rc2` | Docker | <ul><li>[Source code](https://www.nlnetlabs.nl/downloads/unbound/)</li><li>[Source code and CHANGELOGs](https://www.nlnetlabs.nl/projects/unbound/download/)</li></ul> |
| [Knot Resolver](https://www.knot-resolver.cz) | Recursive | `2.0.0`, `2.1.0-2.1.1`, `2.2.0`, `2.3.0`, `2.4.0-2.4.1`, `3.0.0`, `3.1.0`, `3.2.0-3.2.1`, `4.0.0`, `4.1.0`, `4.2.0-4.2.2`, `4.3.0`, `5.0.0-5.0.1`, `5.1.0-5.1.3`, `5.2.0-5.2.1`, `5.3.0-5.3.2`, `5.4.0-5.4.4`, `5.5.0-5.5.3`, `5.6.0`, `5.7.0` | [Official Docker images](https://hub.docker.com/r/cznic/knot-resolver/tags) and custom `Dockerfile`s | <ul><li>[Source Code](https://secure.nic.cz/files/knot-resolver/?C=N;O=D)</li><li>[CHANGELOG](https://gitlab.nic.cz/knot/knot-resolver/-/blob/6.0/NEWS)</li></ul>
| [PowerDNS Recursor](https://www.powerdns.com/powerdns-recursor)| Recursive | `4.8.0-4.8.5`, `4.9.0-4.9.1` | Docker | <ul><li>[Source code](https://downloads.powerdns.com/releases/)</li><li>[Changelogs](https://doc.powerdns.com/recursor/changelog/index.html)</li></ul>|
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
