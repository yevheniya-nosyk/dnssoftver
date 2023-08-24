FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget build-essential libssl-dev libexpat1-dev && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://www.nlnetlabs.nl/downloads/unbound/unbound-1.8.0rc1.tar.gz && tar -xf unbound-1.8.0rc1.tar.gz 

# Build
RUN cd /usr/bin/unbound-1.8.0rc1 && ./configure && make && make install

# Listen on the IPv4 interface
RUN sed -i 's/# interface: 192.0.2.153/interface: 0.0.0.0/g' /usr/local/etc/unbound/unbound.conf
# Allow queries from all the hosts
RUN sed -i 's/# access-control: 127.0.0.0\/8 allow/access-control: 0.0.0.0\/0 allow/g' /usr/local/etc/unbound/unbound.conf
# Do not use unbound username
RUN sed -i 's/# username: "unbound"/username: ""/g' /usr/local/etc/unbound/unbound.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run unbound daemon
CMD ["unbound", "-d"]
