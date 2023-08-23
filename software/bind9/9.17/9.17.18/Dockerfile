FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget xz-utils build-essential libnghttp2-dev libcap-dev libssl-dev libuv1-dev perl pkg-config python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install ply

# Download the source code
RUN cd /usr/bin && wget https://downloads.isc.org/isc/bind9/9.17.18/bind-9.17.18.tar.xz && tar -xf bind-9.17.18.tar.xz 

# Build
RUN cd /usr/bin/bind-9.17.18 && ./configure && make && make install

# Avoid the "named: error while loading shared libraries: libisc" error when running named
ENV LD_LIBRARY_PATH=/usr/local/lib/:$LD_LIBRARY_PATH

# Create the empty configuration file at the default location
RUN touch /usr/local/etc/named.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run named on the foreground
CMD ["named", "-f", "-c", "/usr/local/etc/named.conf"]
