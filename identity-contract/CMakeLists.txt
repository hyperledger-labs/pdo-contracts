# Copyright 2023 Intel Corporation
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

INCLUDE(exchange_common)
LIST(APPEND WASM_LIBRARIES ${EXCHANGE_LIB})
LIST(APPEND WASM_INCLUDES ${EXCHANGE_INCLUDES})

INCLUDE(identity_common.cmake)
LIST(APPEND WASM_LIBRARIES ${IDENTITY_LIB})
LIST(APPEND WASM_INCLUDES ${IDENTITY_INCLUDES})

# -----------------------------------------------------------------
ADD_LIBRARY(${IDENTITY_LIB} STATIC ${IDENTITY_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${IDENTITY_LIB} PUBLIC ${IDENTITY_INCLUDES})

SET_PROPERTY(TARGET ${IDENTITY_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${IDENTITY_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${IDENTITY_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

# -----------------------------------------------------------------
BUILD_CONTRACT(identity contracts/identity.cpp)

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(identity)

# -----------------------------------------------------------------
INCLUDE(Test)
# ADD_SHELL_TEST(identity script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(identity functional SCRIPT test/run_tests.sh)
