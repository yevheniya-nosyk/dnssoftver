FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget curl systemd dotnet7 && rm -rf /var/lib/apt/lists/*

# Download the code
RUN cd /usr/bin && wget https://download.technitium.com/dns/archive/11.2/DnsServerPortable.tar.gz && mkdir DnsServerPortable && tar -xf DnsServerPortable.tar.gz -C /usr/bin/DnsServerPortable

# Expose ports
EXPOSE 53/udp 53/tcp

# Start the server
ENTRYPOINT ["/usr/bin/dotnet", "/usr/bin/DnsServerPortable/DnsServerApp.dll"]
