FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget curl systemd

# Install dotnet
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && apt-get update && apt-get install -y dotnet-sdk-3.1

# Download the code
RUN cd /usr/bin && wget https://download.technitium.com/dns/archive/5.3/DnsServerPortable.tar.gz && mkdir DnsServerPortable && tar -xf DnsServerPortable.tar.gz -C /usr/bin/DnsServerPortable

# Expose ports
EXPOSE 53/udp 53/tcp

# Start the server
ENTRYPOINT ["/usr/bin/dotnet", "/usr/bin/DnsServerPortable/DnsServerApp.dll"]
