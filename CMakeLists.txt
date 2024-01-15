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

CMAKE_MINIMUM_REQUIRED(VERSION 3.16 FATAL_ERROR)

PROJECT(pdo-contracts)
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/exchange-contract")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/digital-asset-contract")
INCLUDE(ProjectVariables)

LIST(APPEND CMAKE_MODULE_PATH "${PDO_SOURCE_ROOT}/contracts/wawaka")
INCLUDE(contract-build)
INCLUDE(wawaka_common)

LIST(APPEND WASM_LIBRARIES ${WW_COMMON_LIB})
LIST(APPEND WASM_INCLUDES ${WW_COMMON_INCLUDES})

SET(CONTRACT_FAMILIES exchange-contract digital-asset-contract identity-contract inference-contract)

# A local cmake file (Local.cmake) allows for local overrides of
# variables. In particular, this is useful to set CONTRACT_FAMILIES
# to just the subset that you want to build/test.
INCLUDE(Local.cmake OPTIONAL)

ENABLE_TESTING()

FOREACH(FAMILY IN ITEMS ${CONTRACT_FAMILIES})
  ADD_SUBDIRECTORY(${FAMILY})
ENDFOREACH()

# -----------------------------------------------------------------
# install the jupyter notebooks, note that the trailing slash here
# is significant and should not be removed; it prevents the notebooks
# directory being prepended to the copied name
# -----------------------------------------------------------------
INCLUDE(Jupyter)
FILE(GLOB_RECURSE NOTEBOOK_SOURCES docs/notebooks/*.py docs/notebooks/*.md)

CONVERT_JUPYTEXT(ROOT_NOTEBOOKS ${NOTEBOOK_SOURCES})

ADD_CUSTOM_TARGET(root-notebooks ALL DEPENDS ${ROOT_NOTEBOOKS})

INSTALL(DIRECTORY docs/notebooks/
  DESTINATION "${PDO_JUPYTER_ROOT}/"
  FILES_MATCHING PATTERN "*.ipynb" PATTERN "*.png")
