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

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget curl systemd dotnet7 && rm -rf /var/lib/apt/lists/*

# Download the code
RUN cd /usr/bin && wget https://download.technitium.com/dns/archive/11.5.2/DnsServerPortable.tar.gz && mkdir DnsServerPortable && tar -xf DnsServerPortable.tar.gz -C /usr/bin/DnsServerPortable

# Expose ports
EXPOSE 53/udp 53/tcp

# Start the server
ENTRYPOINT ["/usr/bin/dotnet", "/usr/bin/DnsServerPortable/DnsServerApp.dll"]
