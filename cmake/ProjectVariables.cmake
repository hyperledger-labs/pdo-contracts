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

# Definitions:
# * PDO_SOURCE_ROOT
# * PDO_INSTALL_ROOT
# * PDO_CONTRACT_VERSION

IF (NOT DEFINED ENV{PDO_SOURCE_ROOT})
  MESSAGE(FATAL_ERROR "PDO_SOURCE_ROOT not defined")
ENDIF()
SET(PDO_SOURCE_ROOT $ENV{PDO_SOURCE_ROOT})

IF (NOT DEFINED ENV{PDO_INSTALL_ROOT})
  MESSAGE(FATAL_ERROR "PDO_INSTALL_ROOT not defined")
ENDIF()
SET(PDO_INSTALL_ROOT $ENV{PDO_INSTALL_ROOT})

SET(PDO_JUPYTER_ROOT ${PDO_INSTALL_ROOT}/opt/pdo/notebooks)

# Get the current version using the get_version
# utility; note that this will provide 0.0.0 as
# the version if something goes wrong (like running
# without any annotated version tags)
EXECUTE_PROCESS(
  COMMAND ./get_version
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
  OUTPUT_VARIABLE PDO_CONTRACT_VERSION
  ERROR_QUIET
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
