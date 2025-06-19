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

# One-stage build
FROM ubuntu:24.04

ARG SOFTWARE_VERSION=6.0.9
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    python3-pip python3-venv git && \
    python3 -m pip install --break-system-packages apkg && \
    apkg system-setup

# Clone and build knot-resolver
RUN git clone --recursive https://gitlab.nic.cz/knot/knot-resolver.git && \
    cd knot-resolver && \
    git checkout tags/v${SOFTWARE_VERSION} && \
    git submodule update --init --recursive && \
    apkg build-dep && \
    apkg build && \
    apkg install

# Modify default config to listen on all interfaces
RUN sed -i "s/- interface: 127.0.0.1@53/- interface: 0.0.0.0@53/g" /etc/knot-resolver/config.yaml

# Expose DNS ports
EXPOSE 53/udp 53/tcp

# Run as knot-resolver user
RUN mkdir -p /run/knot-resolver /var/cache/knot-resolver && \
    chown -R knot-resolver:knot-resolver /run/knot-resolver /var/cache/knot-resolver && \
    chmod 750 /run/knot-resolver /var/cache/knot-resolver
USER knot-resolver

# Run knot-resolver in foreground
CMD ["/usr/bin/knot-resolver"]
