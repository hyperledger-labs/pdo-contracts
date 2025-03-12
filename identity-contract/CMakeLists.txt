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

ADD_CUSTOM_COMMAND(
  OUTPUT ${OPENSSL_WASM_CRYPTO_LIB} ${OPENSSL_WASM_SSL_LIB} ${OPENSSL_WASM_INCLUDE_DIR}
  BYPRODUCTS ${OPENSSL_BUILD_DIR}/${OPENSSL_VERSION}
  COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/openssl/build.sh
  ARGS -o ${OPENSSL_BUILD_DIR}/precompiled -p ${CMAKE_CURRENT_SOURCE_DIR}/openssl/patches -v ${OPENSSL_VERSION}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/openssl/build.sh ${CMAKE_CURRENT_SOURCE_DIR}/openssl/patches/*.patch
  COMMENT "Building OpenSSL for WebAssembly"
)

ADD_CUSTOM_TARGET(
  openssl_wasm
  DEPENDS ${OPENSSL_WASM_CRYPTO_LIB} ${OPENSSL_WASM_SSL_LIB} ${OPENSSL_WASM_INCLUDE_DIR}
)

# -----------------------------------------------------------------
ADD_LIBRARY(${IDENTITY_LIB} STATIC ${IDENTITY_SOURCES})
SET_PROPERTY(TARGET ${IDENTITY_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}" "-Wno-deprecated")
SET_PROPERTY(TARGET ${IDENTITY_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${IDENTITY_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

TARGET_INCLUDE_DIRECTORIES(${IDENTITY_LIB} PUBLIC ${IDENTITY_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${IDENTITY_LIB} PUBLIC ${EXCHANGE_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${IDENTITY_LIB} PUBLIC ${WASM_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${IDENTITY_LIB} PUBLIC ${OPENSSL_WASM_INCLUDE_DIR})

ADD_DEPENDENCIES(${IDENTITY_LIB} openssl_wasm)

# -----------------------------------------------------------------
BUILD_CONTRACT(signature_authority contracts/signature_authority.cpp
  HEADERS ${EXCHANGE_INCLUDES} ${IDENTITY_INCLUDES}
  LIBRARIES ${EXCHANGE_LIB} ${IDENTITY_LIB} ${OPENSSL_WASM_CRYPTO_LIB})

BUILD_CONTRACT(identity contracts/identity.cpp
  HEADERS ${EXCHANGE_INCLUDES} ${IDENTITY_INCLUDES}
  LIBRARIES ${EXCHANGE_LIB} ${IDENTITY_LIB} ${OPENSSL_WASM_CRYPTO_LIB})

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(identity)

# -----------------------------------------------------------------
INCLUDE(Test)
# ADD_SHELL_TEST(identity script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(identity functional SCRIPT test/run_tests.sh)
