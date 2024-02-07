# Build from stratch

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

### Python

This project requires Python 3.10.

Create the virutal environment and install the requirements:

```bash
$ python3 -m virtualenv -p python3.10 .venv
$ source .venv/bin/activate
$ pip3 install -r requirements.txt
```

### Domain name

We need a custom domain to be queried during our tests. By default, we use `dnssoftver.com`.

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

## Signature generation

The script below builds docker images, starts containers in their own network, queries resolvers, processes the responses, generates signatures, and cleans up. Run it:

```bash
$ python3 src/fingerprint.py --repeats <number_of_times_to_repeat_tests>
```

The signatures are stored in `signatures/signatures_[all,minor].json`.

## Classification

We address the classification problem using decision trees built with `scikit-learn`. The following script builds models and saves the text representation of trees to `trees/` and the summary to `models`:

```bash
$ python3 src/build_models.py --granularity [vendor,major,minor,build]
```
