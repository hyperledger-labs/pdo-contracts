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

INCLUDE(Python)
BUILD_WHEEL(exchange)

INCLUDE(Test)
ADD_SHELL_TEST(exchange script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(exchange functional SCRIPT test/run_tests.sh)
