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
    die unable to locate pdo-shell
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
COMMON_CONTRACT_ROOT=${PDO_HOME}/contracts/contracts

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

F_SERVICE_SITE_FILE=${PDO_HOME}/etc/sites/${F_SERVICE_HOST}.toml
if [ ! -f ${F_SERVICE_SITE_FILE} ] ; then
    die unable to locate the service information file ${F_SERVICE_SITE_FILE}; \
        please copy the site.toml file from the service host
fi

F_SERVICE_GROUPS_DB_FILE=${SOURCE_ROOT}/test/${F_SERVICE_HOST}_groups_db
F_SERVICE_DB_FILE=${SOURCE_ROOT}/test/${F_SERVICE_HOST}_db

_COMMON_=("--logfile ${F_LOGFILE}" "--loglevel ${F_LOGLEVEL}")
_COMMON_+=("--ledger ${F_LEDGER_URL}")
_COMMON_+=("--groups-db ${F_SERVICE_GROUPS_DB_FILE}")
_COMMON_+=("--service-db ${F_SERVICE_DB_FILE}")
SHORT_OPTS=${_COMMON_[@]}

_COMMON_+=("--context-file ${F_CONTEXT_FILE}")
OPTS=${_COMMON_[@]}

# -----------------------------------------------------------------
# Make sure the keys and eservice database are created and up to date
# -----------------------------------------------------------------
F_KEY_FILES=()
KEYGEN=${PDO_SOURCE_ROOT}/build/__tools__/make-keys
if [ ! -f ${PDO_HOME}/keys/red_type_private.pem ]; then
    yell create keys for the contracts
    for color in red green blue orange purple white ; do
        ${KEYGEN} --keyfile ${PDO_HOME}/keys/${color}_type --format pem
        ${KEYGEN} --keyfile ${PDO_HOME}/keys/${color}_vetting --format pem
        ${KEYGEN} --keyfile ${PDO_HOME}/keys/${color}_issuer --format pem
        F_KEY_FILES+=(${PDO_HOME}/keys/${color}_{type,vetting,issuer}_{private,public}.pem)
    done

    for color in green1 green2 green3; do
        ${KEYGEN} --keyfile ${PDO_HOME}/keys/${color}_issuer --format pem
        F_KEY_FILES+=(${PDO_HOME}/keys/${color}_issuer_{private,public}.pem)
    done

    ${KEYGEN} --keyfile ${PDO_HOME}/keys/token_type --format pem
    ${KEYGEN} --keyfile ${PDO_HOME}/keys/token_vetting --format pem
    ${KEYGEN} --keyfile ${PDO_HOME}/keys/token_issuer --format pem
    F_KEY_FILES+=(${PDO_HOME}/keys/token_{type,vetting,issuer}_{private,public}.pem)
    for count in 1 2 3 4 5 ; do
        ${KEYGEN} --keyfile ${PDO_HOME}/keys/token_holder${count} --format pem
        F_KEY_FILES+=(${PDO_HOME}/keys/token_holder${count}_{private,public}.pem)
    done
fi

if [ ! -f ${PDO_HOME}/keys/guardian_service.pem ]; then
    yell create keys for the guardian service
    ${KEYGEN} --keyfile ${PDO_HOME}/keys/guardian_service --format pem
    F_KEY_FILES+=(${PDO_HOME}/keys/guardian_service.pem)

    ${KEYGEN} --keyfile ${PDO_HOME}/keys/guardian_sservice --format pem
    F_KEY_FILES+=(${PDO_HOME}/keys/guardian_sservice.pem)
fi

# -----------------------------------------------------------------
function cleanup {
    rm -f ${F_SERVICE_GROUPS_DB_FILE} ${F_SERVICE_GROUPS_DB_FILE}-lock
    rm -f ${F_SERVICE_DB_FILE} ${F_SERVICE_DB_FILE}-lock
    rm -f ${F_CONTEXT_FILE}
    for key_file in ${F_KEY_FILES[@]} ; do
        rm -f ${key_file}
    done

    yell "shutdown guardian and storage service"
    ${COMMON_CONTRACT_ROOT}/scripts/gs_stop.sh
    ${COMMON_CONTRACT_ROOT}/scripts/ss_stop.sh
}

trap cleanup EXIT

# -----------------------------------------------------------------
# Start the guardian service and the storage service
# -----------------------------------------------------------------
try ${COMMON_CONTRACT_ROOT}/scripts/ss_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel debug \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_sservice

sleep 3

try ${COMMON_CONTRACT_ROOT}/scripts/gs_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel debug \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_service \
    --bind host ${F_GUARDIAN_HOST} \
    --bind service_host ${F_SERVICE_HOST}

# -----------------------------------------------------------------
# create the service and groups databases from a site file; the site
# file is assumed to exist in ${PDO_HOME}/etc/sites/${SERVICE_HOST}.toml
#
# by default, the groups will include all available services from the
# service host
# -----------------------------------------------------------------
yell create the service and groups database for host ${F_SERVICE_HOST}
try pdo-service-db import ${SHORT_OPTS} --file ${F_SERVICE_SITE_FILE}
try pdo-eservice create_from_site ${SHORT_OPTS} --file ${F_SERVICE_SITE_FILE} --group default
try pdo-pservice create_from_site ${SHORT_OPTS} --file ${F_SERVICE_SITE_FILE} --group default
try pdo-sservice create_from_site ${SHORT_OPTS} --file ${F_SERVICE_SITE_FILE} --group default \
             --replicas 1 --duration 60

# -----------------------------------------------------------------
# setup the contexts that will be used later for the tests, check this
# -----------------------------------------------------------------
cd "${SOURCE_ROOT}"

rm -f ${CONTEXT_FILE}

try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
    --bind token test1 --bind url http://${F_GUARDIAN_HOST}:7900
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
    --bind token test2 --bind url http://${F_GUARDIAN_HOST}:7900
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
    --bind token test3 --bind url http://${F_GUARDIAN_HOST}:7900

# we need some marbles to use for the exchange transactions
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color blue
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color red
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color green

# and we need the order context
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/order.toml \
           --bind order token1 --bind user token_holder1 \
           --bind offer_count 1 --bind offer_issuer token.test1.token_object.token_1 \
           --bind request_count 20 --bind request_issuer marbles.green.issuer


# -----------------------------------------------------------------
# start the tests
# -----------------------------------------------------------------

yell create a token issuer and mint the tokens
try ex_token_issuer create ${OPTS} --contract token.test1.token_issuer
try inference_token mint_tokens ${OPTS} --contract token.test1.token_object

yell do inference on images
try inference_token do_inference ${OPTS}  --contract token.test1.token_object.token_1 --image "zebra_wiki.jpg"

yell transfer the tokens to the token holders
for i in 1 2 3 4 5 ; do
    try inference_token transfer ${OPTS} \
        --contract token.test1.token_object.token_${i} --new-owner token_holder${i}
done

yell test ownership
inference_token do_inference ${OPTS}  --identity token_issuer \
    --contract token.test1.token_object.token_1 --image "zebra_wiki.jpg"
if [ $? == 0 ]; then
    die should have failed with incorrect owner
fi

try inference_token do_inference ${OPTS} --identity token_holder1 \
    --contract token.test1.token_object.token_1 --image "zebra_wiki.jpg"

#sleep for 10s

exit
