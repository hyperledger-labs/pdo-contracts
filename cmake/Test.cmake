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

# assumes that project variables have been
# set including PDO_INSTALL_ROOT and PDO_CONTRACT_VERSION

# -----------------------------------------------------------------
# Environment Variables
# -----------------------------------------------------------------
SET(TEST_LOG_LEVEL "warn" CACHE STRING "Test log level")
SET(TEST_LOG_FILE "__screen__" CACHE STRING "Test log file")
SET(TEST_SERVICE_HOST "$ENV{PDO_HOSTNAME}" CACHE STRING "Test services host")
SET(TEST_LEDGER "$ENV{PDO_LEDGER_URL}" CACHE STRING "Test ledger URL")

SET(TEST_OPTS
  --loglevel ${TEST_LOG_LEVEL}
  --logfile ${TEST_LOG_FILE}
  --ledger ${TEST_LEDGER}
  --host ${TEST_SERVICE_HOST})

# -----------------------------------------------------------------
# ADD_SHELL_TEST
# -----------------------------------------------------------------
FUNCTION(ADD_SHELL_TEST contract test)
  # ensure that the virtual environment is activated
  SET(ENV{VIRTUAL_ENV} ${PDO_INSTALL_ROOT})

  CMAKE_PARSE_ARGUMENTS(ST "" "SCRIPT" "PARAMS" ${ARGN})
  IF (DEFINED ST_SCRIPT)
    SET(script_file ${ST_SCRIPT})
  ELSE()
    SET(script_file ${CMAKE_CURRENT_SOURCE_DIR}/test/${contract}.psh)
  ENDIF()

  ADD_TEST(
    NAME system-${contract}-${test}
    COMMAND ${script_file} ${TEST_OPTS} ${ST_PARAMS}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
ENDFUNCTION()
