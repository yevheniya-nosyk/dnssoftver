FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget xz-utils build-essential meson ninja-build pkg-config libknot-dev libuv1-dev liblmdb-dev luajit libluajit-5.1-dev && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://secure.nic.cz/files/knot-resolver/knot-resolver-5.7.0.tar.xz && tar -xf knot-resolver-5.7.0.tar.xz

# Build
RUN cd /usr/bin/knot-resolver-5.7.0 && meson setup build_dir && ninja -C build_dir && ninja install -C build_dir

# Listen on the IPv4 interface
RUN sed -i "s/net.listen('127.0.0.1', 53, { kind = 'dns' })/net.listen('0.0.0.0', 53, { kind = 'dns' })/g" /usr/local/etc/knot-resolver/kresd.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/local/sbin/kresd", "-c", "/usr/local/etc/knot-resolver/kresd.conf"]
