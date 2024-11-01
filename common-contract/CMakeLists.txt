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
# Build the library of methods that are defined by the contract
# family. This simplifies sharing the methods with other contract
# families.
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# Build the python wheel that will install all of the contracts in the
# contract family; the contract targets must match the targets used
# to create the contracts above.
# -----------------------------------------------------------------
INCLUDE(Python)
BUILD_WHEEL(contracts)

# -----------------------------------------------------------------
# install the jupyter notebooks, note that the trailing slash here
# is significant and should not be removed; it prevents the notebooks
# directory being prepended to the copied name
# -----------------------------------------------------------------
INCLUDE(Jupyter)
FILE(GLOB_RECURSE NOTEBOOK_SOURCES docs/notebooks/*.py docs/notebooks/*.md)

CONVERT_JUPYTEXT(COMMON_NOTEBOOKS ${NOTEBOOK_SOURCES})

ADD_CUSTOM_TARGET(common-notebooks ALL DEPENDS ${COMMON_NOTEBOOKS})

INSTALL(DIRECTORY docs/notebooks/
  DESTINATION "${PDO_JUPYTER_ROOT}/common"
  FILES_MATCHING PATTERN "*.ipynb" PATTERN "*.png")
