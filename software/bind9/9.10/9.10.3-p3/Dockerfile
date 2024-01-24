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

FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

# Install all the required packages
RUN apt-get update && apt-get install -y wget xz-utils build-essential libcap-dev libssl-dev perl pkg-config python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install ply

# Download the source code
RUN cd /usr/bin && wget https://downloads.isc.org/isc/bind9/9.10.3-P3/bind-9.10.3-P3.tar.gz && tar -xf bind-9.10.3-P3.tar.gz

# Build
RUN cd /usr/bin/bind-9.10.3-P3 && ./configure && make && make install

# Create the empty configuration file at the default location
RUN touch /etc/named.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run named on the foreground
CMD ["named", "-f", "-c", "/etc/named.conf"]
