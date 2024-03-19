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

# -----------------------------------------------------------------
# -----------------------------------------------------------------
: "${PDO_LEDGER_URL?Missing environment variable PDO_LEDGER_URL}"
: "${PDO_HOME?Missing environment variable PDO_HOME}"
: "${PDO_SOURCE_ROOT?Missing environment variable PDO_SOURCE_ROOT}"

# -----------------------------------------------------------------
# -----------------------------------------------------------------

source ${PDO_HOME}/bin/lib/common.sh
check_python_version

if ! command -v pdo-shell &> /dev/null ; then
    yell unable to locate pdo-shell
    exit 1
fi


# -----------------------------------------------------------------
# -----------------------------------------------------------------
if [ "${PDO_LEDGER_TYPE}" == "ccf" ]; then
    if [ ! -f "${PDO_LEDGER_KEY_ROOT}/networkcert.pem" ]; then
        die "CCF ledger keys are missing, please copy and try again"
    fi
fi

# -----------------------------------------------------------------
# Process command line arguments
# -----------------------------------------------------------------
SCRIPTDIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
SOURCE_ROOT="$(realpath ${SCRIPTDIR}/..)"

F_SCRIPT=$(basename ${BASH_SOURCE[-1]} )
F_SERVICE_HOST=${PDO_HOSTNAME}
F_GUARDIAN_HOST=${PDO_HOSTNAME}
F_LEDGER_URL=${PDO_LEDGER_URL}
F_LOGLEVEL=${PDO_LOG_LEVEL:-info}
F_LOGFILE=${PDO_LOG_FILE:-__screen__}
F_CONTEXT_FILE=${SOURCE_ROOT}/test/test_context.toml
F_CONTEXT_TEMPLATES=${PDO_HOME}/contracts/inference/context
F_EXCHANGE_TEMPLATES=${PDO_HOME}/contracts/exchange/context

F_USAGE='--host service-host | --ledger url | --loglevel [debug|info|warn] | --logfile file'
SHORT_OPTS='h:l:'
LONG_OPTS='host:,ledger:,loglevel:,logfile:'

TEMP=$(getopt -o ${SHORT_OPTS} --long ${LONG_OPTS} -n "${F_SCRIPT}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${F_SCRIPT} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -h|--host) F_SERVICE_HOST="$2" ; shift 2 ;;
        -1|--ledger) F_LEDGER_URL="$2" ; shift 2 ;;
        --loglevel) F_LOGLEVEL="$2" ; shift 2 ;;
        --logfile) F_LOGFILE="$2" ; shift 2 ;;
        --help) echo "Usage: ${SCRIPT_NAME} ${F_USAGE}"; exit 0 ;;
        --) shift ; break ;;
        *) echo "Internal error!" ; exit 1 ;;
    esac
done

F_SERVICE_GROUPS_FILE=${SOURCE_ROOT}/test/${F_SERVICE_HOST}_groups.toml
F_SERVICE_DB_FILE=${SOURCE_ROOT}/test/${F_SERVICE_HOST}_db

_COMMON_=("--logfile ${F_LOGFILE}" "--loglevel ${F_LOGLEVEL}")
_COMMON_+=("--ledger ${F_LEDGER_URL}")
_COMMON_+=("--bind service_host ${F_SERVICE_HOST}")
_COMMON_+=("--service-groups ${F_SERVICE_GROUPS_FILE}")
_COMMON_+=("--service-db ${F_SERVICE_DB_FILE}")
_COMMON_+=("--context-file ${F_CONTEXT_FILE}")
OPTS=${_COMMON_[@]}

F_KEY_FILES=()
KEYGEN=${PDO_SOURCE_ROOT}/build/__tools__/make-keys

if [ ! -f ${PDO_HOME}/keys/guardian_service.pem ]; then
    yell create keys for the guardian service
    ${KEYGEN} --keyfile ${PDO_HOME}/keys/guardian_service --format pem
    F_KEY_FILES+=(${PDO_HOME}/keys/guardian_service.pem)

    ${KEYGEN} --keyfile ${PDO_HOME}/keys/guardian_sservice --format pem
    F_KEY_FILES+=(${PDO_HOME}/keys/guardian_sservice.pem)
fi

# -----------------------------------------------------------------
function cleanup {
    rm -f ${F_SERVICE_GROUPS_FILE}
    rm -f ${F_SERVICE_DB_FILE} ${F_SERVICE_DB_FILE}-lock
    rm -f ${F_CONTEXT_FILE}
    for key_file in ${F_KEY_FILES[@]} ; do
        rm -f ${key_file}
    done

    yell "shutdown guardian and storage service"
    ${PDO_HOME}/contracts/inference/scripts/gs_stop.sh
    ${PDO_HOME}/contracts/inference/scripts/ss_stop.sh
}

trap cleanup EXIT

# -----------------------------------------------------------------
# Start the guardian service and the storage service
# -----------------------------------------------------------------
try ${PDO_HOME}/contracts/inference/scripts/ss_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel debug \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_sservice

sleep 3

try ${PDO_HOME}/contracts/inference/scripts/gs_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel debug \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_service \
    --bind host ${F_GUARDIAN_HOST} \
    --bind service_host ${F_SERVICE_HOST}

read -p "Guardian Service Frontend Running. Press any key to exit"
exit
