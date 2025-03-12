#! /bin/bash
# Copyright 2025 Intel Corporation
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

source ${PDO_HOME}/bin/lib/common.sh

OPENSSL_VERSION=3.1.8
PATCH_DIR=${PWD}/patches
OUTPUT_DIR=${PWD}/precompiled

while getopts "o:p:v:" opt; do
    case $opt in
        o)
            OUTPUT_DIR=$OPTARG ;;
        p)
            PATCH_DIR=$OPTARG ;;
        v)
            OPENSSL_VERSION=$OPTARG ;;
        \?)
            die "Invalid option: -$OPTARG" >&2 ;;
    esac
done

# -----------------------------------------------------------------
# Get the openssl source code and unpack it
# -----------------------------------------------------------------
OPENSSL_SOURCE=openssl-${OPENSSL_VERSION}
if [ -d ${OPENSSL_SOURCE} ]; then
    say "OpenSSL source code already exists, skipping download"
else
    say "Downloading OpenSSL source code"
    try wget https://github.com/openssl/openssl/releases/download/${OPENSSL_SOURCE}/${OPENSSL_SOURCE}.tar.gz
    try tar zxf openssl-${OPENSSL_VERSION}.tar.gz
    try rm -f openssl-${OPENSSL_VERSION}.tar.gz
fi

# -----------------------------------------------------------------
# Patch openssl
# -----------------------------------------------------------------
# The following patches are applied to the source code, we use a dry
# run in order to check if the patch is already applied. If it is not
# then apply it

pushd ${OPENSSL_SOURCE}

for patch in ${PATCH_DIR}/*.patch; do
    patch -p1 -N --dry-run --silent <"$patch" >/dev/null 2>/dev/null || continue
    patch -p1 <"$patch"
done

# -----------------------------------------------------------------
# Configure openssl
# -----------------------------------------------------------------
WASI_TOOLKIT_PATH=/opt/wasi-sdk/bin
if [ ! -d ${WASI_TOOLKIT_PATH} ]; then
    say "WASI toolkit not found at ${WASI_TOOLKIT_PATH}, please install it"
    exit 1
fi

# First set up the paths to the wasi toolkit install
export AR="${WASI_TOOLKIT_PATH}/llvm-ar"
export RANLIB="${WASI_TOOLKIT_PATH}/llvm-ranlib"
export CC="${WASI_TOOLKIT_PATH}/clang"
export CXX="${WASI_TOOLKIT_PATH}/clang++"

# Now specify the OpenSSL configuration options, these options are mix of selections from SGX SSL and
# from https://github.com/jedisct1/openssl-wasm
EXTRA_CPP_FLAGS="-D_BSD_SOURCE -D_WASI_EMULATED_GETPID -DOPENSSL_SMALL_FOOTPRINT -DNO_SYSLOG"
EXTRA_CPP_FLAGS="${EXTRA_CPP_FLAGS} -Dgetuid=getpagesize -Dgeteuid=getpagesize -Dgetgid=getpagesize -Dgetegid=getpagesize"

# Disable building tests in the library
DISABLE_TESTS="no-tests no-buildtest-c++ no-external-tests no-unit-test"

# Disable features; these are inspired by the SGX SSL configuration options
# Earlier versions of openssl can include 'no-atexit' but 3.1.0 requires a
# different workaround
DISABLE_FOR_SGX="no-autoalginit no-cms no-dsa no-err no-filenames no-rdrand no-zlib"

# Prep for WASM; these are inspired by https://github.com/jedisct1/openssl-wasm
DISABLE_FOR_WASM="no-asm no-async no-egd no-ktls no-module no-posix-io no-secure-memory no-shared no-sock"
DISABLE_FOR_WASM="${DISABLE_FOR_WASM} no-stdio no-threads no-ui-console no-weak-ssl-ciphers"

# Set up the environment variables for the build
export CROSS_COMPILE=""
export CFLAGS="-Ofast -Werror -Qunused-arguments -Wno-shift-count-overflow"
export CPPFLAGS="${CPPFLAGS} ${EXTRA_CPP_FLAGS}"
export CXXFLAGS="-Werror -Qunused-arguments -Wno-shift-count-overflow"
export LDFLAGS="-s -lwasi-emulated-getpid"
try ./Configure --banner="wasm32-wasi port" ${DISABLE_TESTS} ${DISABLE_FOR_SGX} ${DISABLE_FOR_WASM} wasm32-wasi

# -----------------------------------------------------------------
# Build the library
# -----------------------------------------------------------------
NUM_CORES=$(grep -c '^processor' /proc/cpuinfo)
if [ "$NUM_CORES " == " " ]; then
    NUM_CORES=4
fi

try make "-j${NUM_CORES}"

# -----------------------------------------------------------------
# Install the library and include files
# -----------------------------------------------------------------
popd

mkdir -p ${OUTPUT_DIR}/lib
mv ${OPENSSL_SOURCE}/*.a ${OUTPUT_DIR}/lib

mkdir -p ${OUTPUT_DIR}/include
cp -r ${OPENSSL_SOURCE}/include/openssl ${OUTPUT_DIR}/include
