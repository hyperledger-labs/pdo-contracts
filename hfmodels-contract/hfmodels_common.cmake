# Copyright 2024 Intel Corporation
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
SET (HFMODELS_INCLUDES ${WASM_INCLUDES})
LIST(APPEND HFMODELS_INCLUDES ${EXCHANGE_INCLUDES})
LIST(APPEND HFMODELS_INCLUDES ${CMAKE_CURRENT_LIST_DIR})

# ---------------------------------------------
# Set up the default source list
# ---------------------------------------------
FILE(GLOB HFMODELS_COMMON_SOURCE ${CMAKE_CURRENT_LIST_DIR}/hfmodels/common/*.cpp)
FILE(GLOB HFMODELS_CONTRACT_SOURCE ${CMAKE_CURRENT_LIST_DIR}/hfmodels/contracts/*.cpp)

SET (HFMODELS_SOURCES)
LIST(APPEND HFMODELS_SOURCES ${HFMODELS_COMMON_SOURCE})
LIST(APPEND HFMODELS_SOURCES ${HFMODELS_CONTRACT_SOURCE})

# ---------------------------------------------
# Build the wawaka contract common library
# ---------------------------------------------
SET(HFMODELS_LIB ww_hfmodels)
