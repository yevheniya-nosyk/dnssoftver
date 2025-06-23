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

ARG SOFTWARE_VERSION=3.1.0
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git build-essential pkg-config autoconf libtool libknot-dev \
    libuv1-dev libcmocka-dev libluajit-5.1-dev bsdmainutils \
    lua-socket lua-sec liburcu-dev libedit-dev

# Build and install Knot DNS 2.7.8 (libknot)
RUN git clone --recursive https://gitlab.nic.cz/knot/knot-dns.git && \
    cd knot-dns && \
    git checkout tags/v2.7.8 && \
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
    ln -s /usr/include/luajit-2.1 /usr/local/include/lua5.1 && \
    # git submodule update --init --recursive && \
    PKG_CONFIG_PATH="/tmp/knot/lib/pkgconfig" && \
    CFLAGS="-I/tmp/knot/include" \
    LDFLAGS="-L/tmp/knot/lib" \
    make LUA_CFLAGS="-I/usr/include/luajit-2.1" && \
    make install

# Stage 2: Run
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# Avoid the "kresd: error while loading shared libraries: libkres.so ..." error 
ENV LD_LIBRARY_PATH=/usr/local/lib:/tmp/knot/lib/

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    libcap-ng0 libluajit-5.1-2 libgnutls30 libuv1 \
    liblmdb0 libsystemd0 libnghttp2-14 lua-socket lua-sec && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy built artifacts
COPY --from=builder /tmp/knot /tmp/knot
COPY --from=builder /usr/local /usr/local

# Update the configuration file
RUN sed -i \
    "s/-- net = { '127.0.0.1', '::1' }/net.listen('0.0.0.0', 53, { kind = 'dns' })/g" \
    /usr/local/etc/knot-resolver/config.personal
RUN sed -i "/user('knot-resolver', 'knot-resolver')/d" \
    /usr/local/etc/knot-resolver/config.personal

EXPOSE 53/udp 53/tcp

CMD ["/usr/local/sbin/kresd", "-c", "/usr/local/etc/knot-resolver/config.personal"]
