# Copyright 2019 Intel Corporation
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

ifndef PDO_INSTALL_ROOT
$(error Incomplete configuration, PDO_INSTALL_ROOT is not defined)
endif

ifndef PDO_HOME
$(error Incomplete configuration, PDO_HOME is not defined)
endif

SOURCE_ROOT ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

WAMR_ROOT=${PDO_SOURCE_ROOT}/interpreters/wasm-micro-runtime
WAMR_TOOLCHAIN=$(WAMR_ROOT)/wamr-sdk/app/wasi_toolchain.cmake
WASI_SDK_DIR=/opt/wasi-sdk

TEST_LOG_LEVEL ?= warn
TEST_LOG_FILE ?= __screen__
TEST_SERVICE_HOST ?= $(PDO_HOSTNAME)
TEST_LEDGER ?= $(PDO_LEDGER_URL)

VERSION=${shell ${SOURCE_ROOT}/bin/get_version}

all : contracts

build :
	@ cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=$(WAMR_TOOLCHAIN)

contracts : build
	@ cmake --build build

install : contracts
	@ cmake --install build

test : install
	@ cmake -B build \
		-DCMAKE_TOOLCHAIN_FILE=$(WAMR_TOOLCHAIN) \
		-DTEST_LOG_LEVEL=$(TEST_LOG_LEVEL) \
		-DTEST_LOG_FILE=$(TEST_LOG_FILE) \
		-DTEST_LEDGER=$(TEST_LEDGER) \
		-DTEST_SERVICE_HOST=$(TEST_SERVICE_HOST)
	@ make -C build test ARGS='-V'

clean :
	@ echo Remove build directory
	@ if [ -d $(SOURCE_ROOT)/build ]; then \
		make -C build clean; \
		rm -rf build; \
	fi
	@ echo Clean up python caches
	@ find . -iname '*.pyc' -delete
	@ find . -iname '__pycache__' -delete

.PHONY : all clean contracts install uninstall test
