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
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/exchange-contract")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/digital-asset-contract")
MESSAGE("CMAKE PATH: ${CMAKE_MODULE_PATH}")
INCLUDE(ProjectVariables)

LIST(APPEND CMAKE_MODULE_PATH "${PDO_SOURCE_ROOT}/contracts/wawaka")
INCLUDE(contract-build)
INCLUDE(wawaka_common)

LIST(APPEND WASM_LIBRARIES ${WW_COMMON_LIB})
LIST(APPEND WASM_INCLUDES ${WW_COMMON_INCLUDES})

ENABLE_TESTING()

ADD_SUBDIRECTORY(exchange-contract)
ADD_SUBDIRECTORY(digital-asset-contract)
