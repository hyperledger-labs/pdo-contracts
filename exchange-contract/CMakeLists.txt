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

# -----------------------------------------------------------------
ADD_LIBRARY(${EXCHANGE_LIB} STATIC ${EXCHANGE_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${EXCHANGE_LIB} PUBLIC ${EXCHANGE_INCLUDES})

SET_PROPERTY(TARGET ${EXCHANGE_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${EXCHANGE_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${EXCHANGE_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

# -----------------------------------------------------------------
BUILD_CONTRACT(asset_type contracts/asset_type.cpp)
BUILD_CONTRACT(vetting_organization contracts/vetting_organization.cpp)
BUILD_CONTRACT(issuer contracts/issuer.cpp)
BUILD_CONTRACT(exchange contracts/exchange.cpp)

BUILD_CONTRACT(data_guardian contracts/data_guardian.cpp)
BUILD_CONTRACT(token_issuer contracts/token_issuer.cpp)
BUILD_CONTRACT(token_object contracts/token_object.cpp)

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(exchange)

# -----------------------------------------------------------------
INCLUDE(Test)
ADD_SHELL_TEST(exchange script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(exchange functional SCRIPT test/run_tests.sh)
