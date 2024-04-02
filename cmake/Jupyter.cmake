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


SET(JUPYTEXT "${PDO_INSTALL_ROOT}/bin/jupytext" CACHE STRING "Path to the Jupytext command")
IF(NOT EXISTS ${JUPYTEXT})
  MESSAGE(FATAL_ERROR "${JUPYTEXT} not found; please install with '${PDO_INSTALL_ROOT}/bin/pip install jupytext'")
ENDIF()

FUNCTION(CONVERT_JUPYTEXT NOTEBOOKS)
  SET(RESULT)

  FOREACH (JUPYTEXT_FILE ${ARGN})
    GET_FILENAME_COMPONENT(SOURCE_DIR ${JUPYTEXT_FILE} DIRECTORY)
    GET_FILENAME_COMPONENT(BASENAME ${JUPYTEXT_FILE} NAME_WLE)
    SET(NOTEBOOK_FILE "${BASENAME}.ipynb")

    ADD_CUSTOM_COMMAND(
      OUTPUT ${SOURCE_DIR}/${NOTEBOOK_FILE}
      COMMAND ${JUPYTEXT}
      ARGS --to notebook ${JUPYTEXT_FILE}
      WORKING_DIRECTORY ${SOURCE_DIR}
      DEPENDS ${JUPYTEXT_FILE}
      COMMENT "Convert ${JUPYTEXT_FILE} to ${NOTEBOOK_FILE}"
      )

    LIST(APPEND RESULT ${SOURCE_DIR}/${NOTEBOOK_FILE})
  ENDFOREACH()

  SET(${NOTEBOOKS} ${RESULT} PARENT_SCOPE)

ENDFUNCTION()
