FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget libboost-dev libboost-filesystem-dev libboost-serialization-dev libboost-system-dev libboost-thread-dev libboost-context-dev libboost-test-dev libssl-dev libboost-test-dev g++ make pkg-config liblua5.2-dev libluajit-5.1-dev && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://downloads.powerdns.com/releases/pdns-recursor-4.0.5-rc1.tar.bz2 && tar -xf pdns-recursor-4.0.5-rc1.tar.bz2

# Build
RUN cd /usr/bin/pdns-recursor-4.0.5-rc1 && ./configure && make && make install

# Avoid the problem with socket directory
RUN mkdir /var/run/pdns-recursor

# Expose ports
EXPOSE 53/udp 53/tcp

# Run pdns-recursor with some options
CMD ["/usr/local/sbin/pdns_recursor", "--allow-from=0.0.0.0/0", "--local-address=0.0.0.0"]
