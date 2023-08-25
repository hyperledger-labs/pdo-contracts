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

PLUGINS_WHL_FILE=dist/pdo_exchange-$(VERSION)-py3-none-any.whl
PLUGIN_SOURCE=$(shell cat MANIFEST)

all : $(PLUGINS_WHL_FILE)

build :
	@ cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=$(WAMR_TOOLCHAIN)

contracts : build
	@ cmake --build ./build

$(PLUGINS_WHL_FILE) : contracts $(PLUGIN_SOURCE)
	@ echo Build plugins package, note this expects python3 build module is installed
	@ $(PDO_INSTALL_ROOT)/bin/python3 -m build --wheel

clean :
	@ echo Remove plugin builds
	@ $(PDO_INSTALL_ROOT)/bin/python3 setup.py clean --all
	@ rm -rf $(SOURCE_ROOT)/dist $(SOURCE_ROOT)/*.egg-info
	@ echo Remove build directory
	@ if [ -d $(SOURCE_ROOT)/build ]; then \
		cmake --build $(SOURCE_ROOT)/build --target clean; \
		rm -rf $(SOURCE_ROOT)/build; \
	fi
	@ echo Clean up python caches
	@ find . -iname '*.pyc' -delete
	@ find . -iname '__pycache__' -delete

install : $(PLUGINS_WHL_FILE)
	@ echo Install the python wheel
	@ $(PDO_INSTALL_ROOT)/bin/pip install --upgrade $(PLUGINS_WHL_FILE)
	@ echo Install the resources
	@ $(PDO_INSTALL_ROOT)/bin/pdo-install-plugin-resources --module pdo.exchange --family exchange

uninstall :
	- . $(abspath $(PDO_INSTALL_ROOT)/bin/activate) && pip uninstall --yes $(PLUGINS_WHL_FILE)

test :
	@ . $(abspath $(PDO_INSTALL_ROOT)/bin/activate) && \
		test/run_tests.sh --loglevel $(TEST_LOG_LEVEL) --logfile $(TEST_LOG_FILE) \
			--host $(TEST_SERVICE_HOST) --ledger $(TEST_LEDGER)
	@ . $(abspath $(PDO_INSTALL_ROOT)/bin/activate) && \
		test/script_test.sh --loglevel $(TEST_LOG_LEVEL) --logfile $(TEST_LOG_FILE) \
			--host $(TEST_SERVICE_HOST) --ledger $(TEST_LEDGER)

.PHONY : all clean contracts install uninstall test
