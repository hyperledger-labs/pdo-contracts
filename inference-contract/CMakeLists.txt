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

ADD_LIBRARY(${INFERENCE_LIB} STATIC ${INFERENCE_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${INFERENCE_LIB} PUBLIC ${INFERENCE_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${INFERENCE_LIB} PUBLIC ${EXCHANGE_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${INFERENCE_LIB} PUBLIC ${WASM_INCLUDES})

SET_PROPERTY(TARGET ${INFERENCE_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${INFERENCE_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${INFERENCE_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

BUILD_CONTRACT(inference_token_object contracts/token_object.cpp
  HEADERS ${EXCHANGE_INCLUDES} ${INFERENCE_INCLUDES}
  LIBRARIES ${EXCHANGE_LIB} ${INFERENCE_LIB})

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
