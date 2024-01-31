#!/bin/bash
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

source /project/pdo/tools/environment.sh
source ${PDO_HOME}/bin/lib/common.sh

# to get build without (ignored) errors
export PDO_HOSTNAME=localhost
export PDO_LEDGER_URL=https://127.0.0.1:6600

check_pdo_build_env

# -----------------------------------------------------------------
yell activate the PDO environment
# -----------------------------------------------------------------
. ${PDO_INSTALL_ROOT}/bin/activate

# -----------------------------------------------------------------
yell create client configuration files
# -----------------------------------------------------------------

# this could be pushed out to the runtime; however, the installation tools
# need a configuration for the loggers. so we will create a set of keys here
# that can be overwritten later if necessary; note that the test scripts all
# assume that the user[0-9] keys exist.
try ${PDO_INSTALL_ROOT}/bin/pdo-configure-users -t ${PDO_SOURCE_ROOT}/build/template -o ${PDO_HOME} \
    --key-count 10 --key-base user --host ${PDO_HOSTNAME}

# -----------------------------------------------------------------
yell build the the contracts
# -----------------------------------------------------------------
try make -C /project/pdo/contracts contracts
try make -C /project/pdo/contracts install

# -----------------------------------------------------------------
yell add some contract specific functions to the PDO install
# -----------------------------------------------------------------
mkdir -p ${PDO_INSTALL_ROOT}/opt/pdo/etc/context
