#!/usr/bin/env bash
set -x
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BIN_DIR=$SCRIPT_DIR/../bin/

rm -rf /tmp/bloaty-root
mkdir /tmp/bloaty-root
cd /tmp/bloaty-root

git clone --recursive git@github.com:google/bloaty.git
mkdir build
mkdir install
cmake -B build -G Ninja -S bloaty -DCMAKE_INSTALL_PREFIX=/tmp/bloaty-root/install -DCMAKE_BUILD_TYPE=RELEASE
cmake --build build
cmake --build build --target install
cp -t $BIN_DIR /tmp/bloaty-root/install/bin/bloaty
