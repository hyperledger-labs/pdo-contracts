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

# This is necessary to get at the definitions necessary
# for the std::string class
INCLUDE(exchange_common)
LIST(APPEND WASM_LIBRARIES ${EXCHANGE_LIB})
LIST(APPEND WASM_INCLUDES ${EXCHANGE_INCLUDES})


INCLUDE(inference_common.cmake)
LIST(APPEND WASM_LIBRARIES ${INFERENCE_LIB})
LIST(APPEND WASM_INCLUDES ${INFERENCE_INCLUDES})

ADD_LIBRARY(${INFERENCE_LIB} STATIC ${INFERENCE_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${INFERENCE_LIB} PUBLIC ${INFERENCE_INCLUDES})

SET_PROPERTY(TARGET ${INFERENCE_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${INFERENCE_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${INFERENCE_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

BUILD_CONTRACT(inference_token_object contracts/token_object.cpp)

# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(inference inference_token_object)

# -----------------------------------------------------------------
INCLUDE(Test)
ADD_SHELL_TEST(inference script SCRIPT test/script_test.sh)

# -----------------------------------------------------------------
# install the jupyter notebooks, note that the trailing slash here
# is significant and should not be removed; it prevents the notebooks
# directory being prepended to the copied name
# -----------------------------------------------------------------

INCLUDE(Jupyter)
FILE(GLOB_RECURSE NOTEBOOK_SOURCES docs/notebooks/*.py docs/notebooks/*.md)

CONVERT_JUPYTEXT(INFERENCE_NOTEBOOKS ${NOTEBOOK_SOURCES})

ADD_CUSTOM_TARGET(inference-notebooks ALL DEPENDS ${INFERENCE_NOTEBOOKS})

INSTALL(DIRECTORY docs/notebooks/
  DESTINATION "${PDO_JUPYTER_ROOT}/inference"
  FILES_MATCHING PATTERN "*.ipynb")
