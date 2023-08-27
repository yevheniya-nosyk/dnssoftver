FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y python3-pip git
RUN pip3 install apkg
RUN apkg system-setup

# Download the source code
RUN cd /usr/bin && git clone --recursive https://gitlab.nic.cz/knot/knot-resolver.git && cd /usr/bin/knot-resolver && git checkout tags/v5.7.0

# Build
RUN cd /usr/bin/knot-resolver && apkg build-dep && apkg build && apkg install

# Listen on the IPv4 interface
RUN sed -i "s/net.listen('127.0.0.1', 53, { kind = 'dns' })/net.listen('0.0.0.0', 53, { kind = 'dns' })/g" /etc/knot-resolver/kresd.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/sbin/kresd", "-c", "/etc/knot-resolver/kresd.conf"]
