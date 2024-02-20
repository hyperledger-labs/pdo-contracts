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


# This is necessary to get at the definitions necessary
# for the std::string class
INCLUDE(exchange_common)
LIST(APPEND WASM_LIBRARIES ${EXCHANGE_LIB})
LIST(APPEND WASM_INCLUDES ${EXCHANGE_INCLUDES})

INCLUDE(da_common)
LIST(APPEND WASM_LIBRARIES ${DIGITAL_ASSET_LIB})
LIST(APPEND WASM_INCLUDES ${DIGITAL_ASSET_INCLUDES})

# -----------------------------------------------------------------
ADD_LIBRARY(${DIGITAL_ASSET_LIB} STATIC ${DIGITAL_ASSET_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${DIGITAL_ASSET_LIB} PUBLIC ${DIGITAL_ASSET_INCLUDES})

SET_PROPERTY(TARGET ${DIGITAL_ASSET_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${DIGITAL_ASSET_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${DIGITAL_ASSET_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

# -----------------------------------------------------------------
BUILD_CONTRACT(da_guardian contracts/guardian.cpp)
BUILD_CONTRACT(da_token_object contracts/token_object.cpp)

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(digital_asset da_guardian da_token_object)

# -----------------------------------------------------------------
INCLUDE(Test)
ADD_SHELL_TEST(digital-asset script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(digital-asset functional SCRIPT test/run_tests.sh)

# -----------------------------------------------------------------
# install the jupyter notebooks, note that the trailing slash here
# is significant and should not be removed; it prevents the notebooks
# directory being prepended to the copied name
# -----------------------------------------------------------------
INSTALL(DIRECTORY docs/notebooks/
  DESTINATION "${PDO_JUPYTER_ROOT}/digital-asset"
  FILES_MATCHING PATTERN "*.ipynb")
