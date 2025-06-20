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
FROM ubuntu:24.04 AS builder

ARG SOFTWARE_VERSION=5.7.3
ENV DEBIAN_FRONTEND=noninteractive

# Install all the required packages to build
RUN apt-get update && apt-get install -y \
    ninja-build meson build-essential pkg-config libknot-dev libluajit-5.1-dev \
    luajit libuv1-dev liblmdb-dev libsystemd-dev libjemalloc-dev \
    libgnutls28-dev git cmake libnghttp2-dev libssl-dev libcap-ng-dev

# Download the source code and build
RUN git clone --recursive https://gitlab.nic.cz/knot/knot-resolver.git && \
    cd knot-resolver && \
    git checkout tags/v${SOFTWARE_VERSION} && \
    git submodule update --init --recursive && \
    meson setup build_dir --prefix=/tmp/kr --default-library=static && \
    ninja -C build_dir && \
    ninja install -C build_dir

# Stage 2: Run
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Only install runtime dependencies
RUN apt-get update && apt-get install -y \
    libcap-ng0 libluajit-5.1-2 libgnutls30 libuv1 liblmdb0 \
    libjemalloc2 libsystemd0 libknot14  libzscanner4 libnghttp2-14 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=builder /tmp/kr /tmp/kr

# Create the configuration file
RUN mkdir -p /etc/knot-resolver && \
    echo "net.listen('0.0.0.0')" > /etc/knot-resolver/kresd.conf

# Expose ports
EXPOSE 53/udp 53/tcp

# Run knot-resolver
CMD ["/tmp/kr/sbin/kresd", "-c", "/etc/knot-resolver/kresd.conf"]
