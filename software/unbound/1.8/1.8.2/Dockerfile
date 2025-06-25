# Copyright 2025 Yevheniya Nosyk
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

# Stage 1: Build
FROM ubuntu:18.04 AS builder

ARG SOFTWARE_VERSION=1.8.2
ENV DEBIAN_FRONTEND=noninteractive

# Install all the required packages to build
RUN apt-get update && apt-get install -y \
    wget build-essential libssl-dev libexpat1-dev bison flex && \
    rm -rf /var/lib/apt/lists/*

# Download the source code and build
WORKDIR /build
RUN wget https://www.nlnetlabs.nl/downloads/unbound/unbound-${SOFTWARE_VERSION}.tar.gz && \
    tar -xf unbound-${SOFTWARE_VERSION}.tar.gz && \
    cd unbound-${SOFTWARE_VERSION} && \
    ./configure && make && make install

# Stage 2: Run
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# Only install runtime dependencies
RUN apt-get update && apt-get install -y libssl1.1 && \
    rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=builder /usr/local /usr/local

# Listen on the IPv4 interface
RUN sed -i 's/# interface: 192.0.2.153/interface: 0.0.0.0/g' /usr/local/etc/unbound/unbound.conf
# Allow queries from all the hosts
RUN sed -i 's/# access-control: 127.0.0.0\/8 allow/access-control: 0.0.0.0\/0 allow/g' /usr/local/etc/unbound/unbound.conf
# Do not use unbound username
RUN sed -i 's/# username: "unbound"/username: ""/g' /usr/local/etc/unbound/unbound.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run unbound daemon
CMD ["unbound", "-d"]