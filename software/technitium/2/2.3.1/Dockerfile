# Copyright 2023 Yevheniya Nosyk
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget curl systemd

# Install dotnet
RUN wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && apt-get update && apt-get install -y dotnet-sdk-2.2

# Download the code
RUN cd /usr/bin && wget https://download.technitium.com/dns/archive/2.3.1/DnsServerPortable.tar.gz && mkdir DnsServerPortable && tar -xf DnsServerPortable.tar.gz -C /usr/bin/DnsServerPortable

# Expose ports
EXPOSE 53/udp 53/tcp

# Start the server
ENTRYPOINT ["/usr/bin/dotnet", "/usr/bin/DnsServerPortable/DnsServerApp.dll"]
