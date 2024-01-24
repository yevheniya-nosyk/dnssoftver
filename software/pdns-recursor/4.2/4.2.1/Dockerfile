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
RUN apt-get update && apt-get install -y wget libboost-dev libboost-filesystem-dev libboost-serialization-dev libboost-system-dev libboost-thread-dev libboost-context-dev libboost-test-dev libssl-dev libboost-test-dev g++ make pkg-config libluajit-5.1-dev && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://downloads.powerdns.com/releases/pdns-recursor-4.2.1.tar.bz2 && tar -xf pdns-recursor-4.2.1.tar.bz2

# Build
RUN cd /usr/bin/pdns-recursor-4.2.1 && ./configure && make && make install

# Avoid the problem with socket directory
RUN mkdir /var/run/pdns-recursor

# Create the configuration file
RUN pdns_recursor -config >> /usr/local/etc/recursor.conf
RUN echo "allow-from=0.0.0.0/0" >> /usr/local/etc/recursor.conf
RUN echo "local-address=0.0.0.0" >> /usr/local/etc/recursor.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run pdns-recursor with some options
CMD ["/usr/local/sbin/pdns_recursor", "--allow-from=0.0.0.0/0", "--local-address=0.0.0.0"]
