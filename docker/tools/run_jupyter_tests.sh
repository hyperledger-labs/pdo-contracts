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
F_SERVICE_HOST=
F_INTERFACE=localhost
F_PORT=8888

F_USAGE='-i|--interface [hostname] -1|--ledger [url] -p|--port [port] -s|--service-host [hostname]'
SHORT_OPTS='i:l:p:s:'
LONG_OPTS='interface:,ledger:,port:,service-host:'

TEMP=$(getopt -o ${SHORT_OPTS} --long ${LONG_OPTS} -n "${SCRIPT_NAME}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${SCRIPT_NAME} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -i|--interface) F_INTERFACE="$2" ; shift 2 ;;
        -l|--ledger) F_LEDGER_URL="$2" ; shift 2 ;;
        -p|--port) F_PORT="$2" ; shift 2 ;;
        -s|--service-host) F_SERVICE_HOST="$2" ; shift 2 ;;
        --help) echo "Usage: ${SCRIPT_NAME} ${F_USAGE}"; exit 0 ;;
    	--) shift ; break ;;
    	*) echo "Internal error!" ; exit 1 ;;
    esac
done

if [ -z "${F_SERVICE_HOST}" ]; then
    die Missing required parameter: service-host
fi

if [ -z "${F_LEDGER_URL}" ]; then
    die Missing required parameter: ledger
fi

# The client only uses PDO_HOSTNAME to create the initial configuration
# file. Since the notebook will override this for each operation, we
# just leave it set to localhost
export PDO_HOSTNAME=${F_SERVICE_HOST}
export PDO_LEDGER_URL=${F_LEDGER_URL}

export no_proxy=$PDO_HOSTNAME,$no_proxy
export NO_PROXY=$PDO_HOSTNAME,$NO_PROXY

check_pdo_runtime_env

# -----------------------------------------------------------------
# activate the virtual environment
# -----------------------------------------------------------------
. ${PDO_INSTALL_ROOT}/bin/activate

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

# site.toml is a way to notify that the services are running;
# in addition, the client uses the information to load the
# services and groups database; we create an initial
# default database from this information
F_SERVICE_SITE_FILE=${PDO_HOME}/etc/sites/${F_SERVICE_HOST}.toml
mkdir -p $(dirname ${F_SERVICE_SITE_FILE})

while [ ! -f ${XFER_DIR}/services/etc/site.toml ]; do
    say "waiting for site configuration"
    sleep 5
done

try cp ${XFER_DIR}/services/etc/site.toml ${F_SERVICE_SITE_FILE}
try pdo-service-db import --file ${F_SERVICE_SITE_FILE}
try pdo-eservice create_from_site --file ${F_SERVICE_SITE_FILE} --group default
try pdo-pservice create_from_site --file ${F_SERVICE_SITE_FILE} --group default
try pdo-sservice create_from_site --file ${F_SERVICE_SITE_FILE} --group default --replicas 1 --duration 60

# -----------------------------------------------------------------
# Handle the configuration of the services
# -----------------------------------------------------------------
yell configure client for ledger $PDO_LEDGER_URL
try ${PDO_INSTALL_ROOT}/bin/pdo-configure-users -t ${PDO_SOURCE_ROOT}/build/template -o ${PDO_HOME} \
    --key-count 10 --key-base user

# -----------------------------------------------------------------
yell start the jupyter server
# -----------------------------------------------------------------
export SHELL=/bin/bash          # make bash the default shell for jupyter launcher
export PDO_JUPYTER_ROOT=${PDO_INSTALL_ROOT}/opt/pdo/notebooks

cd ${PDO_JUPYTER_ROOT}
jupyter lab --no-browser --port=${F_PORT} --ServerApp.ip=${F_INTERFACE}
