FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget curl systemd mono-complete

# Download the code
RUN cd /usr/bin && wget https://download.technitium.com/dns/archive/1.1/DnsServerPortable.tar.gz && mkdir DnsServerPortable && tar -xf DnsServerPortable.tar.gz -C /usr/bin/DnsServerPortable

# Expose ports
EXPOSE 53/udp 53/tcp

# Start the server
ENTRYPOINT ["/usr/bin/mono", "/usr/bin/DnsServerPortable/DnsServer/DnsServerApp.exe"]
