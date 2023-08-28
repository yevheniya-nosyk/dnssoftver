FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget build-essential pkg-config libknot-dev libuv1-dev libcmocka-dev libluajit-5.1-dev bsdmainutils && rm -rf /var/lib/apt/lists/*

# Avoid the "kresd: error while loading shared libraries: libkres.so.7: cannot open shared object file: No such file or directory" error when running kresd
ENV LD_LIBRARY_PATH=/usr/local/lib/:$LD_LIBRARY_PATH

# Download the source code
RUN cd /usr/bin && wget https://secure.nic.cz/files/knot-resolver/knot-resolver-2.2.0.tar.xz && tar -xf knot-resolver-2.2.0.tar.xz 

# Build
RUN cd /usr/bin/knot-resolver-2.2.0 && make && make install

# Listen on the IPv4 interface
RUN sed -i "s/-- net = { '127.0.0.1', '::1' }/net.listen('0.0.0.0', 53, { kind = 'dns' })/g" /usr/local/etc/knot-resolver/config.personal
RUN sed -i "/user('knot-resolver', 'knot-resolver')/d" /usr/local/etc/knot-resolver/config.personal
RUN sed -i "s#root.keys#usr/bin/knot-resolver-2.2.0/distro/common/root.keys#" /usr/local/etc/knot-resolver/config.personal

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/local/sbin/kresd", "-c", "/usr/local/etc/knot-resolver/config.personal", "-v"]
