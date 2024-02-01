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
F_MODE=build
F_SERVICE_HOST=

F_USAGE='-1|--ledger [url] -m|--mode [build|copy|skip] -s|--service-host [hostname]'
SHORT_OPTS='l:m:s:'
LONG_OPTS='ledger:,mode:,service-host:'

TEMP=$(getopt -o ${SHORT_OPTS} --long ${LONG_OPTS} -n "${SCRIPT_NAME}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${SCRIPT_NAME} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -l|--ledger) F_LEDGER_URL="$2" ; shift 2 ;;
        -m|--mode) F_MODE="$2" ; shift 2 ;;
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

export PDO_HOSTNAME=${F_SERVICE_HOST}
export PDO_LEDGER_URL=${F_LEDGER_URL}

export no_proxy=$PDO_HOSTNAME,$no_proxy
export NO_PROXY=$PDO_HOSTNAME,$NO_PROXY

check_pdo_runtime_env

# -----------------------------------------------------------------
yell copy ledger keys
# -----------------------------------------------------------------
if [ ! -f ${XFER_DIR}/ccf/keys/networkcert.pem ]; then
    die "unable to locate ledger keys"
fi
mkdir -p ${PDO_LEDGER_KEY_ROOT}/
try cp ${XFER_DIR}/ccf/keys/networkcert.pem ${PDO_LEDGER_KEY_ROOT}/

# -----------------------------------------------------------------
# Handle the configuration of the services
# -----------------------------------------------------------------
if [ "${F_MODE,,}" == "build" ]; then
    yell configure client for host $PDO_HOSTNAME and ledger $PDO_LEDGER_URL
    try ${PDO_INSTALL_ROOT}/bin/pdo-configure-users -t ${PDO_SOURCE_ROOT}/build/template -o ${PDO_HOME} \
        --key-count 10 --key-base user --host ${PDO_HOSTNAME}
elif [ "${F_MODE,,}" == "copy" ]; then
    yell copy the configuration from xfer/client/etc and xfer/client/keys
    mkdir -p ${PDO_HOME}/etc ${PDO_HOME}/keys
    cp ${XFER_DIR}/client/etc/* ${PDO_HOME}/etc/
    cp ${XFER_DIR}/client/keys/* ${PDO_HOME}/keys/
elif [ "${F_MODE,,}" == "skip" ]; then
    yell start with existing configuration
else
    die "invalid restart mode; ${F_MODE}"
fi

# -----------------------------------------------------------------
# -----------------------------------------------------------------
export NOTEBOOK_ROOT=/project/pdo/notebooks

if [ ${F_MODE} == 'build' ]; then
    # clean out any existing notebooks
    rm -rf ${NOTEBOOK_ROOT}/*

    # create the directory tree
    mkdir -p ${NOTEBOOK_ROOT}
    mkdir -p ${NOTEBOOK_ROOT}/factories
    mkdir -p ${NOTEBOOK_ROOT}/instances
    mkdir -p ${NOTEBOOK_ROOT}/templates

    if [ -f /project/pdo/contracts/exchange-contract/docs/notebooks/index.ipynb ] ; then
        cp /project/pdo/contracts/exchange-contract/docs/notebooks/index.ipynb ${NOTEBOOK_ROOT}
    fi
    cp /project/pdo/contracts/exchange-contract/docs/notebooks/factories/*.ipynb ${NOTEBOOK_ROOT}/factories
    cp /project/pdo/contracts/exchange-contract/docs/notebooks/templates/*.ipynb ${NOTEBOOK_ROOT}/templates
fi

# -----------------------------------------------------------------
yell run the service test suite
# -----------------------------------------------------------------
. ${PDO_INSTALL_ROOT}/bin/activate

cd /project/pdo/notebooks
jupyter lab --no-browser --port=8888
