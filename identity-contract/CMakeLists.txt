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

INCLUDE(family.cmake)
INCLUDE(exchange-contract/methods)
INCLUDE(methods.cmake)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
SET(OPENSSL_BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR})
SET(OPENSSL_VERSION 3.1.0)

SET(OPENSSL_WASM_INCLUDE_DIR ${OPENSSL_BUILD_DIR}/precompiled/include)
SET(OPENSSL_WASM_LIB_DIR ${OPENSSL_BUILD_DIR}/precompiled/lib)
SET(OPENSSL_WASM_CRYPTO_LIB ${OPENSSL_WASM_LIB_DIR}/libcrypto.a)
SET(OPENSSL_WASM_SSL_LIB ${OPENSSL_WASM_LIB_DIR}/libssl.a)
SET(OPENSSL_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src/packages/openssl)

ADD_CUSTOM_COMMAND(
  OUTPUT ${OPENSSL_WASM_CRYPTO_LIB} ${OPENSSL_WASM_SSL_LIB} ${OPENSSL_WASM_INCLUDE_DIR}
  BYPRODUCTS ${OPENSSL_BUILD_DIR}/${OPENSSL_VERSION}
  COMMAND ${OPENSSL_SOURCE_DIR}/build.sh
  ARGS -o ${OPENSSL_BUILD_DIR}/precompiled -p ${OPENSSL_SOURCE_DIR}/patches -v ${OPENSSL_VERSION}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS ${OPENSSL_SOURCE_DIR}/build.sh ${OPENSSL_SOURCE_DIR}/patches/*.patch
  COMMENT "Building OpenSSL for WebAssembly"
)

ADD_CUSTOM_TARGET(
  openssl_wasm
  DEPENDS ${OPENSSL_WASM_CRYPTO_LIB} ${OPENSSL_WASM_SSL_LIB} ${OPENSSL_WASM_INCLUDE_DIR}
)

# -----------------------------------------------------------------
ADD_LIBRARY(${${CF_HANDLE}_LIB} STATIC ${${CF_HANDLE}_SOURCES})
SET_PROPERTY(TARGET ${${CF_HANDLE}_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}" "-Wno-deprecated")
SET_PROPERTY(TARGET ${${CF_HANDLE}_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${${CF_HANDLE}_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${${CF_HANDLE}_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${EXCHANGE_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${WASM_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${OPENSSL_WASM_INCLUDE_DIR})

ADD_DEPENDENCIES(${${CF_HANDLE}_LIB} openssl_wasm)

# -----------------------------------------------------------------
FOREACH(contract ${CF_CONTRACTS})
  MESSAGE(NOTICE "Building contract ${contract}")
  BUILD_CONTRACT(${CF_NAME}_${contract} src/contracts/${contract}.cpp
    HEADERS ${EXCHANGE_INCLUDES} ${${CF_HANDLE}_INCLUDES}
    LIBRARIES ${EXCHANGE_LIB} ${${CF_HANDLE}_LIB} ${OPENSSL_WASM_CRYPTO_LIB}
  )
ENDFOREACH()

# -----------------------------------------------------------------
INCLUDE(Python)
LIST(TRANSFORM CF_CONTRACTS PREPEND ${CF_NAME}_ OUTPUT_VARIABLE expanded_contracts)
BUILD_WHEEL(${CF_NAME} ${expanded_contracts})

# -----------------------------------------------------------------
INCLUDE(Test)
# ADD_SHELL_TEST(identity script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(${CF_NAME} functional SCRIPT test/run_tests.sh)
