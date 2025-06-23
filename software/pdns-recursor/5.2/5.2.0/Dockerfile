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
FROM ubuntu:22.04 AS builder

ARG SOFTWARE_VERSION=5.2.0
ENV DEBIAN_FRONTEND=noninteractive

# Install all the required packages to build
RUN apt-get update && apt-get install -y \
    wget libboost-dev libboost-filesystem-dev libboost-serialization-dev \
    libboost-system-dev libboost-thread-dev libboost-context-dev \
    libboost-test-dev libssl-dev libboost-test-dev g++ make pkg-config \
    libluajit-5.1-dev cargo && \
    rm -rf /var/lib/apt/lists/*

# Download the source code and build
WORKDIR /build
RUN wget https://downloads.powerdns.com/releases/pdns-recursor-${SOFTWARE_VERSION}.tar.bz2 && \
    tar -xf pdns-recursor-${SOFTWARE_VERSION}.tar.bz2 && \
    cd pdns-recursor-${SOFTWARE_VERSION} && \
    ./configure && make && make install

# Stage 2: Run
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Only install runtime dependencies
RUN apt-get update && apt-get install -y \
    libboost-filesystem1.74.0  libboost-serialization1.74.0 \
    libboost-system1.74.0 libboost-thread1.74.0 libssl3 \
    libboost-context1.74.0 libluajit-5.1-2 && \
    rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=builder /usr/local /usr/local

# Avoid the problem with socket directory
RUN mkdir /var/run/pdns-recursor

# Expose ports
EXPOSE 53/udp 53/tcp

# Run pdns-recursor with some options
CMD ["/usr/local/sbin/pdns_recursor", "--allow-from=0.0.0.0/0", "--local-address=0.0.0.0"]
