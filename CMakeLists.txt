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

CMAKE_MINIMUM_REQUIRED(VERSION 3.10 FATAL_ERROR)

PROJECT(pdo-contracts)

IF (NOT DEFINED ENV{PDO_SOURCE_ROOT})
  MESSAGE(FATAL_ERROR "PDO_SOURCE_ROOT not defined")
ENDIF()
SET(PDO_SOURCE_ROOT $ENV{PDO_SOURCE_ROOT})

IF (NOT DEFINED ENV{PDO_INSTALL_ROOT})
  MESSAGE(FATAL_ERROR "PDO_INSTALL_ROOT not defined")
ENDIF()
SET(PDO_INSTALL_ROOT $ENV{PDO_INSTALL_ROOT})

INCLUDE(${PDO_SOURCE_ROOT}/contracts/wawaka/contract-build.cmake)
INCLUDE(${PDO_SOURCE_ROOT}/contracts/wawaka/wawaka_common.cmake)

LIST(APPEND WASM_LIBRARIES ${WW_COMMON_LIB})
LIST(APPEND WASM_INCLUDES ${WW_COMMON_INCLUDES})

EXECUTE_PROCESS(
  COMMAND ./get_version
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin
  OUTPUT_VARIABLE CONTRACT_VERSION
  ERROR_QUIET
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

ENABLE_TESTING()

ADD_SUBDIRECTORY(exchange-contract)
