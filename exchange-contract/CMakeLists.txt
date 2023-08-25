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

INCLUDE(exchange_common.cmake)

LIST(APPEND WASM_LIBRARIES ${EXCHANGE_LIB})
LIST(APPEND WASM_INCLUDES ${EXCHANGE_INCLUDES})

SET(CONTRACT_INSTALL_DIRECTORY "${PDO_HOME}/contracts/exchange")

BUILD_CONTRACT(asset_type contracts/asset_type.cpp)
BUILD_CONTRACT(vetting_organization contracts/vetting_organization.cpp)
BUILD_CONTRACT(issuer contracts/issuer.cpp)
BUILD_CONTRACT(exchange contracts/exchange.cpp)

BUILD_CONTRACT(data_guardian contracts/data_guardian.cpp)
BUILD_CONTRACT(token_issuer contracts/token_issuer.cpp)
BUILD_CONTRACT(token_object contracts/token_object.cpp)

SET(PYTHON "${PDO_INSTALL_ROOT}/bin/python3")
SET(PIP "${PDO_INSTALL_ROOT}/bin/pip3")
SET(WHEEL_FILE "pdo_exchange-${CONTRACT_VERSION}-py3-none-any.whl")
SET(WHEEL_PATH "${CMAKE_BINARY_DIR}/dist")
FILE(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/MANIFEST" MANIFEST)

# adding the build and egg-info directories to the output means that
# they will be cleaned up with the global clean target
ADD_CUSTOM_COMMAND(
  OUTPUT ${WHEEL_PATH}/${WHEEL_FILE} ${CMAKE_CURRENT_SOURCE_DIR}/build ${CMAKE_CURRENT_SOURCE_DIR}/pdo_exchange.egg-info
  COMMAND ${PYTHON}
  ARGS -m build --wheel --outdir ${WHEEL_PATH}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  DEPENDS ${MANIFEST})

ADD_CUSTOM_TARGET(exchange-package ALL DEPENDS ${WHEEL_PATH}/${WHEEL_FILE})

STRING(JOIN "\n" INSTALL_COMMAND
  "MESSAGE(\"RUNNING INSTALL\")"
  "EXECUTE_PROCESS(COMMAND ${PIP} install --upgrade ${WHEEL_PATH}/${WHEEL_FILE})"
  "EXECUTE_PROCESS(COMMAND ${PDO_INSTALL_ROOT}/bin/pdo-install-plugin-resources --module pdo.exchange --family exchange)")

MESSAGE("INSTALL COMMAND: ${INSTALL_COMMAND}")
INSTALL(CODE ${INSTALL_COMMAND})

SET(TEST_LOG_LEVEL "warn" CACHE STRING "Test log level")
SET(TEST_LOG_FILE "__screen__" CACHE STRING "Test log file")
SET(TEST_SERVICE_HOST $ENV{PDO_HOSTNAME} CACHE STRING "Test services host")
SET(TEST_LEDGER $ENV{PDO_LEDGER_URL} CACHE STRING "Test ledger URL")

SET(TEST_OPTS
  --loglevel ${TEST_LOG_LEVEL}
  --logfile ${TEST_LOG_FILE}
  --ledger ${TEST_LEDGER}
  --host ${TEST_SERVICE_HOST})

ADD_TEST(
  NAME exchange-script
  COMMAND script_test.sh ${TEST_OPTS}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test)

ADD_TEST(
  NAME exchange-functional
  COMMAND run_tests.sh ${TEST_OPTS}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test)
