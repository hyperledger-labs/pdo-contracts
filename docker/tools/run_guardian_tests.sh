#!/bin/bash
# Copyright 2024 Intel Corporation
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

SCRIPT_NAME=$(basename ${BASH_SOURCE[-1]} )

source /project/pdo/tools/environment.sh
source ${PDO_HOME}/bin/lib/common.sh

# -----------------------------------------------------------------
# Process command line arguments
# -----------------------------------------------------------------
F_LEDGER_URL=
F_LOGLEVEL=info
F_MODE=build
F_INTERFACE=localhost

F_USAGE='-i|--interface [hostname] -1|--ledger [url] --loglevel [debug|info|warn] -m|--mode [build|copy|skip]'
SHORT_OPTS='i:l:m:'
LONG_OPTS='interface:,ledger:,loglevel:,mode:'

TEMP=$(getopt -o ${SHORT_OPTS} --long ${LONG_OPTS} -n "${SCRIPT_NAME}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${SCRIPT_NAME} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -i|--interface) F_INTERFACE="$2" ; shift 2 ;;
        -l|--ledger) F_LEDGER_URL="$2" ; shift 2 ;;
        -m|--mode) F_MODE="$2" ; shift 2 ;;
        --loglevel) F_LOGLEVEL="--loglevel $2" ; shift 2 ;;
        --help) echo "Usage: ${SCRIPT_NAME} ${F_USAGE}"; exit 0 ;;
    	--) shift ; break ;;
    	*) echo "Internal error!" ; exit 1 ;;
    esac
done

if [ -z "${F_LEDGER_URL}" ]; then
    die Missing required parameter: ledger
fi

# The client only uses PDO_HOSTNAME to create the initial configuration
# file. Since the notebook will override this for each operation, we
# just leave it set to localhost
export PDO_HOSTNAME=localhost
export PDO_LEDGER_URL=${F_LEDGER_URL}

export no_proxy=$PDO_HOSTNAME,$no_proxy
export NO_PROXY=$PDO_HOSTNAME,$NO_PROXY

check_pdo_runtime_env

# -----------------------------------------------------------------
yell copy ledger keys
# -----------------------------------------------------------------
# need to wait for the ledger to get going so we can grab the
# keys and copy them into the correct location, in theory the
# healthcheck in the docker-compose configuration file should
# ensure that the keys are already present
mkdir -p ${PDO_LEDGER_KEY_ROOT}
while [ ! -f ${XFER_DIR}/ccf/keys/networkcert.pem ]; do
    say "waiting for ledger keys"
    sleep 5
done
try cp ${XFER_DIR}/ccf/keys/networkcert.pem ${PDO_LEDGER_KEY_ROOT}/

# for now the site.toml is just a way to notify
# that the services are running; in the future
# the client should be able to incorporate this
# file and begin to use the information, again
# in theory this should be taken care of by the
# health checks in the docker compose configuration
while [ ! -f ${XFER_DIR}/services/etc/site.toml ]; do
    say "waiting for site configuration"
    sleep 5
done

try cp ${XFER_DIR}/services/etc/site.toml ${PDO_HOME}/etc/site.toml

# -----------------------------------------------------------------
function cleanup {
    yell "shutdown guardian and storage service"
    ${PDO_HOME}/contracts/inference/scripts/gs_stop.sh
    ${PDO_HOME}/contracts/inference/scripts/ss_stop.sh
}

trap cleanup EXIT

# -----------------------------------------------------------------
# Start the guardian service and the storage service
# -----------------------------------------------------------------
try ${PDO_HOME}/contracts/inference/scripts/ss_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel ${F_LOGLEVEL} \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_sservice

try ${PDO_HOME}/contracts/inference/scripts/gs_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel ${F_LOGLEVEL} \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_service \
    --bind host ${F_INTERFACE}

sleep infinity
