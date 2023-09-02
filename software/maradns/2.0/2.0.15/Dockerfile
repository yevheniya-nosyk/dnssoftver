FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget build-essential && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://maradns.samiam.org/download/2.0/2.0.15/maradns-2.0.15.tar.bz2 && tar -xf maradns-2.0.15.tar.bz2

# Update the paths
RUN sed -i 's#/usr/local/share/man/man1#/usr/share/man/man1#g' /usr/bin/maradns-2.0.15/build/install.locations
RUN sed -i 's#/usr/local/share/man/man5#/usr/share/man/man5#g' /usr/bin/maradns-2.0.15/build/install.locations
RUN sed -i 's#/usr/local/share/man/man8#/usr/share/man/man8#g' /usr/bin/maradns-2.0.15/build/install.locations

# Build
RUN cd /usr/bin/maradns-2.0.15 && ./configure && make && make install

# Update the configuration file
RUN sed -i 's/bind_address="127.0.0.2"/bind_address="0.0.0.0"/g' /etc/dwood3rc
RUN sed -i 's/recursive_acl = "127.0.0.1\/16"/recursive_acl = "0.0.0.0\/0"/g' /etc/dwood3rc
RUN sed -i 's/#root_servers/root_servers/g' /etc/dwood3rc

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/local/sbin/Deadwood"]
