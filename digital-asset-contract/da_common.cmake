# Copyright 2022 Intel Corporation
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

IF(NOT DEFINED EXCHANGE_INCLUDES)
  MESSAGE(FATAL_ERROR "EXCHANGE_INCLUDES is not defined")
ENDIF()

# ---------------------------------------------
# Set up the include list
# ---------------------------------------------
SET (DIGITAL_ASSET__INCLUDES ${WASM_INCLUDES})
LIST(APPEND DIGITAL_ASSET_INCLUDES ${EXCHANGE_INCLUDES})
LIST(APPEND DIGITAL_ASSET_INCLUDES ${CMAKE_CURRENT_LIST_DIR})

# ---------------------------------------------
# Set up the default source list
# ---------------------------------------------
FILE(GLOB DIGITAL_ASSET_COMMON_SOURCE ${CMAKE_CURRENT_LIST_DIR}/digital_asset/common/*.cpp)
FILE(GLOB DIGITAL_ASSET_CONTRACT_SOURCE ${CMAKE_CURRENT_LIST_DIR}/digital_asset/contracts/*.cpp)

SET (DIGITAL_ASSET_SOURCES)
LIST(APPEND DIGITAL_ASSET_SOURCES ${DIGITAL_ASSET_COMMON_SOURCE})
LIST(APPEND DIGITAL_ASSET_SOURCES ${DIGITAL_ASSET_CONTRACT_SOURCE})

# ---------------------------------------------
# Build the wawaka contract common library
# ---------------------------------------------
SET(DIGITAL_ASSET_LIB ww_digital_asset)
