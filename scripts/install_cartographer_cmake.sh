#!/bin/sh

# Copyright 2016 The Cartographer Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o verbose

# Build and install Cartographer.
# cd cartographer
mkdir -p build
cd build
# cmake .. -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake .. -G Ninja -DBUILD_PROMETHEUS=ON  -DCMAKE_INSTALL_PREFIX=/opt/tong/prefix
ninja
CTEST_OUTPUT_ON_FAILURE=1 ninja test
sudo ninja install
