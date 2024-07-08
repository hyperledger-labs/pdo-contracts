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

# This is necessary to get at the definitions necessary
# for the std::string class
INCLUDE(exchange_common)
LIST(APPEND WASM_LIBRARIES ${EXCHANGE_LIB})
LIST(APPEND WASM_INCLUDES ${EXCHANGE_INCLUDES})


INCLUDE(hfmodels_common.cmake)
LIST(APPEND WASM_LIBRARIES ${HFMODELS_LIB})
LIST(APPEND WASM_INCLUDES ${HFMODELS_INCLUDES})

ADD_LIBRARY(${HFMODELS_LIB} STATIC ${HFMODELS_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${HFMODELS_LIB} PUBLIC ${HFMODELS_INCLUDES})

SET_PROPERTY(TARGET ${HFMODELS_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${HFMODELS_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${HFMODELS_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

BUILD_CONTRACT(hfmodels_token_object contracts/token_object.cpp)

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(hfmodels hfmodels_token_object)