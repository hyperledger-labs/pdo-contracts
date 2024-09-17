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

# -----------------------------------------------------------------
# If you are building an independent contract family using the
# standard paths, you should not need to change anything below.
# Information about the contract family should be set in family.cmake
# -----------------------------------------------------------------
INCLUDE(family.cmake)
INCLUDE(methods.cmake)

# -----------------------------------------------------------------
# Build the library of methods that are defined by the contract
# family. This simplifies sharing the methods with other contract
# families.
# -----------------------------------------------------------------
ADD_LIBRARY(${${CF_HANDLE}_LIB} STATIC ${${CF_HANDLE}_SOURCES})
TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${${CF_HANDLE}_INCLUDES})
TARGET_INCLUDE_DIRECTORIES(${${CF_HANDLE}_LIB} PUBLIC ${WASM_INCLUDES})

SET_PROPERTY(TARGET ${${CF_HANDLE}_LIB} APPEND_STRING PROPERTY COMPILE_OPTIONS "${WASM_BUILD_OPTIONS}")
SET_PROPERTY(TARGET ${${CF_HANDLE}_LIB} APPEND_STRING PROPERTY LINK_OPTIONS "${WASM_LINK_OPTIONS}")
SET_TARGET_PROPERTIES(${${CF_HANDLE}_LIB} PROPERTIES EXCLUDE_FROM_ALL TRUE)

# -----------------------------------------------------------------
# Add a build target for each of the contracts; to ensure uniqueness
# prepend the name of the contract family to the name of the contract
# -----------------------------------------------------------------
FOREACH(contract ${CF_CONTRACTS})
  BUILD_CONTRACT(${CF_NAME}_${contract} src/contracts/${contract}.cpp
    HEADERS ${${CF_HANDLE}_INCLUDES}
    LIBRARIES ${${CF_HANDLE}_LIB}
  )
ENDFOREACH()

# -----------------------------------------------------------------
# Build the python wheel that will install all of the contracts in the
# contract family; the contract targets must match the targets used
# to create the contracts above.
# -----------------------------------------------------------------
INCLUDE(Python)
LIST(TRANSFORM CF_CONTRACTS PREPEND ${CF_NAME}_ OUTPUT_VARIABLE expanded_contracts)
BUILD_WHEEL(${CF_NAME} ${expanded_contracts})

# -----------------------------------------------------------------
INCLUDE(Test)
ADD_SHELL_TEST(${CF_NAME} script SCRIPT test/script_test.sh)
ADD_SHELL_TEST(${CF_NAME} functional SCRIPT test/run_tests.sh)

# -----------------------------------------------------------------
# install the jupyter notebooks, note that the trailing slash here
# is significant and should not be removed; it prevents the notebooks
# directory being prepended to the copied name
# -----------------------------------------------------------------
INCLUDE(Jupyter)
FILE(GLOB_RECURSE NOTEBOOK_SOURCES docs/notebooks/*.py docs/notebooks/*.md)
CONVERT_JUPYTEXT(EX_NOTEBOOKS ${NOTEBOOK_SOURCES})

ADD_CUSTOM_TARGET(${CF_NAME}-notebooks ALL DEPENDS ${EX_NOTEBOOKS})

INSTALL(DIRECTORY docs/notebooks/
  DESTINATION "${PDO_JUPYTER_ROOT}/${CF_NAME}"
  FILES_MATCHING PATTERN "*.ipynb" PATTERN "files/*" )
