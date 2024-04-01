#!/bin/bash

# Copyright 2022 Intel Corporation
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
SCRIPTDIR="$(dirname $(readlink --canonicalize ${BASH_SOURCE}))"
SOURCE_ROOT="$(realpath ${SCRIPTDIR}/..)"

F_SCRIPT=$(basename ${BASH_SOURCE[-1]} )
F_SERVICE_HOST=${PDO_HOSTNAME}
F_LEDGER_URL=${PDO_LEDGER_URL}
F_LOGLEVEL=${PDO_LOG_LEVEL:-info}
F_LOGFILE=${PDO_LOG_FILE:-__screen__}
F_CONTEXT_FILE=${SOURCE_ROOT}/test/test_context.toml
F_CONTEXT_TEMPLATES=${PDO_HOME}/contracts/digital_asset/context
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

# -----------------------------------------------------------------
function cleanup {
    rm -f ${F_SERVICE_GROUPS_DB_FILE} ${F_SERVICE_GROUPS_DB_FILE}-lock
    rm -f ${F_SERVICE_DB_FILE} ${F_SERVICE_DB_FILE}-lock
    rm -f ${F_CONTEXT_FILE}
    for key_file in ${F_KEY_FILES[@]} ; do
        rm -f ${key_file}
    done
}

trap cleanup EXIT

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
# setup the contexts that will be used later for the tests
# -----------------------------------------------------------------
cd "${SOURCE_ROOT}"

rm -f ${F_CONTEXT_FILE}

yell create the context for the marbles and tokens and objects
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
    --bind token da_test_100 --bind image_file ${SOURCE_ROOT}/test/images/test-100x100.bmp
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
	   --bind token da_test_10 --bind image_file ${SOURCE_ROOT}/test/images/test-10x10.bmp
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
	   --bind token da_test_5 --bind image_file ${SOURCE_ROOT}/test/images/test-5x5.bmp
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml \
	   --bind token da_test_almaden --bind image_file ${SOURCE_ROOT}/test/images/almaden.bmp

# we need some marbles to use for the exchange transactions
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color blue
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color red
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/marbles.toml --bind color green

# and we need the order context
try pdo-context load ${OPTS} --import-file ${F_EXCHANGE_TEMPLATES}/order.toml \
           --bind order token1 --bind user token_holder1 \
           --bind offer_count 1 --bind offer_issuer token.da_test_100.token_object.token_1 \
           --bind request_count 20 --bind request_issuer marbles.green.issuer

# -----------------------------------------------------------------
# start the tests
# -----------------------------------------------------------------

# -----------------------------------------------------------------
yell create the marble issuers we need and issue assets to the users
for color in blue red green ; do
    yell create ${color} issuer
    try ex_issuer create ${OPTS} --contract marbles.${color}.issuer
    try ex_issuer approve_issuer ${OPTS} --contract marbles.${color}.vetting --issuer marbles.${color}.issuer
    try ex_issuer initialize_issuer ${OPTS} --contract marbles.${color}.issuer
    for i in 1 2 3 4 5 ; do
        try ex_issuer issue_assets ${OPTS} --contract marbles.${color}.issuer \
            --owner user${i} --count "$((10 * ${i}))"
    done
done

# -----------------------------------------------------------------
yell create a token issuer and mint the tokens for 100x100 image
try da_guardian create ${OPTS} --contract token.da_test_100.guardian
try ex_token_issuer create ${OPTS} --contract token.da_test_100.token_issuer
try ex_token_object mint_tokens ${OPTS} --contract token.da_test_100.token_object

yell transfer the tokens to the token holders
for i in 1 2 3 4 5 ; do
    try da_token transfer ${OPTS} \
        --contract token.da_test_100.token_object.token_${i} --new-owner token_holder${i}
done

yell get the metadata from the objects
for i in 1 2 3 4 5 ; do
    da_token get_image_metadata ${OPTS} --identity token_holder${i} \
        --contract token.da_test_100.token_object.token_${i}
done

# -----------------------------------------------------------------
yell take a look at the balances before the exchange
try ex_issuer balance ${OPTS} --contract marbles.green.issuer --identity user3

yell create the exchange
try ex_exchange create_order ${OPTS} --contract order.token1 --verbose
try ex_exchange examine ${OPTS} --contract order.token1 --verbose
try ex_exchange match_order ${OPTS} --contract order.token1 --identity user3 --verbose
try ex_exchange claim_payment ${OPTS} --contract order.token1 --verbose
try ex_exchange claim_offer ${OPTS} --contract order.token1 --identity user3 --verbose

yell take a look at the balances after the exchange
try ex_issuer balance ${OPTS} --contract marbles.green.issuer --identity token_holder1
try ex_issuer balance ${OPTS} --contract marbles.green.issuer --identity user3

exit

# -----------------------------------------------------------------
# -----------------------------------------------------------------
## Almaden image is too big and crashes the eservice; we need to figure out why
## the service crashes and how to prevent AND we need to figure out how to pass
## the image when its big (e.g. use a KV store)
say create a token issuer and mint the tokens for almaden image
try ex_create_token_issuer ${OPTS} --contract token.da_test_almaden.token_issuer
try ex_mint_tokens ${OPTS} --contract token.da_test_almaden.token_object

say transfer the tokens to the token holders
for i in 1 2 3 4 5 ; do
    try ex_transfer_assets ${OPTS} \
        --contract token.da_test_almaden.token_object.token_${i} --new-owner token_holder${i}
done
say get the metadata from the objects
for i in 1 2 3 4 5 ; do
    da_token get_image_metadata ${OPTS} --identity token_holder${i} \
        --contract token.da_test_almaden.token_object.token_${i}
done
