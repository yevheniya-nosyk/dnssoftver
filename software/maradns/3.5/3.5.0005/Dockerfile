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

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget build-essential && rm -rf /var/lib/apt/lists/*

# Download the source code
RUN cd /usr/bin && wget https://maradns.samiam.org/download/3.5/3.5.0005/maradns-3.5.0005.tar.xz && tar -xf maradns-3.5.0005.tar.xz

# Build
RUN cd /usr/bin/maradns-3.5.0005 && ./configure && make && make install

# Update the configuration file
RUN sed -i 's/bind_address="127.0.0.2"/bind_address="0.0.0.0"/g' /etc/dwood3rc
RUN sed -i 's/recursive_acl = "127.0.0.1\/16"/recursive_acl = "0.0.0.0\/0"/g' /etc/dwood3rc
RUN sed -i 's/#root_servers/root_servers/g' /etc/dwood3rc

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/local/sbin/Deadwood"]
