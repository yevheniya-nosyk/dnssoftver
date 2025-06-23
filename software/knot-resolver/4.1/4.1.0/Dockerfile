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
FROM ubuntu:20.04 AS builder

ARG SOFTWARE_VERSION=4.1.0
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential autoconf libtool pkg-config \
    ninja-build meson git bison flex \
    libluajit-5.1-dev luajit libuv1-dev liblmdb-dev \
    libsystemd-dev libjemalloc-dev libgnutls28-dev \
    libnghttp2-dev libssl-dev libcap-ng-dev liburcu-dev libedit-dev

# Build and install Knot DNS 2.8.1 (libknot)
RUN git clone --recursive https://gitlab.nic.cz/knot/knot-dns.git && \
    cd knot-dns && \
    git checkout tags/v2.8.1 && \
    autoreconf -i -f && \
    ./configure --prefix=/tmp/knot && \
    make -j$(nproc) && \
    make install

# Export paths so knot-resolver finds custom libknot
ENV PKG_CONFIG_PATH=/tmp/knot/lib/pkgconfig
ENV LD_LIBRARY_PATH=/tmp/knot/lib

# Build and install Knot Resolver
RUN git clone --recursive https://gitlab.nic.cz/knot/knot-resolver.git && \
    cd knot-resolver && \
    git checkout tags/v${SOFTWARE_VERSION} && \
    PKG_CONFIG_PATH="/tmp/knot/lib/pkgconfig" && \
    CFLAGS="-I/tmp/knot/include" \
    LDFLAGS="-L/tmp/knot/lib" \
    meson setup build_dir --prefix=/tmp/kr --default-library=static && \
    ninja -C build_dir && \
    ninja install -C build_dir

# Stage 2: Run
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/tmp/knot/lib

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    libcap-ng0 libluajit-5.1-2 libgnutls30 libuv1 \
    liblmdb0 libjemalloc2 libsystemd0 libnghttp2-14 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy built artifacts
COPY --from=builder /tmp/knot /tmp/knot
COPY --from=builder /tmp/kr /tmp/kr

# Update the configuration file
RUN sed -i \
    "s/net.listen('127.0.0.1')/net.listen('0.0.0.0')/g" \
    /tmp/kr/etc/knot-resolver/kresd.conf
RUN sed -i "/user('knot-resolver', 'knot-resolver')/d" \
    /tmp/kr/etc/knot-resolver/kresd.conf

EXPOSE 53/udp 53/tcp

CMD ["/tmp/kr/sbin/kresd", "-c", "/tmp/kr/etc/knot-resolver/kresd.conf"]
