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
RUN apt-get update && apt-get install -y wget build-essential pkg-config libknot-dev libuv1-dev libcmocka-dev libluajit-5.1-dev bsdmainutils && rm -rf /var/lib/apt/lists/*

# Avoid the "kresd: error while loading shared libraries: libkres.so.7: cannot open shared object file: No such file or directory" error when running kresd
ENV LD_LIBRARY_PATH=/usr/local/lib/:$LD_LIBRARY_PATH

# Download the source code
RUN cd /usr/bin && wget https://secure.nic.cz/files/knot-resolver/knot-resolver-2.1.1.tar.xz && tar -xf knot-resolver-2.1.1.tar.xz 

# Build
RUN cd /usr/bin/knot-resolver-2.1.1 && make && make install

# Listen on the IPv4 interface
RUN sed -i "s/-- net = { '127.0.0.1', '::1' }/net.listen('0.0.0.0', 53, { kind = 'dns' })/g" /usr/local/etc/knot-resolver/config.personal
RUN sed -i "/user('knot-resolver', 'knot-resolver')/d" /usr/local/etc/knot-resolver/config.personal
RUN sed -i "s#root.keys#/usr/local/etc/knot-resolver/root.keys#" /usr/local/etc/knot-resolver/config.personal
RUN echo ". 0 IN DS 19036 8 2 49AAC11D7B6F6446702E54A1607371607A1A41855200FD2CE1CDDE32F24E8FB5" >> /usr/local/etc/knot-resolver/root.keys
RUN echo ". 0 IN DS 20326 8 2 E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D" >> /usr/local/etc/knot-resolver/root.keys

# Expose ports
EXPOSE 53/udp 53/tcp

# Run 
CMD ["/usr/local/sbin/kresd", "-c", "/usr/local/etc/knot-resolver/config.personal", "-v"]
