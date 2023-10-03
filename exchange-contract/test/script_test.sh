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
F_LEDGER_URL=${PDO_LEDGER_URL}
F_LOGLEVEL=${PDO_LOG_LEVEL:-info}
F_LOGFILE=${PDO_LOG_FILE:-__screen__}
F_CONTEXT_FILE=${SOURCE_ROOT}/test/test_context.toml
F_CONTEXT_TEMPLATES=${PDO_HOME}/contracts/exchange/context

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
    rm -f ${F_SERVICE_GROUPS_FILE}
    rm -f ${F_SERVICE_DB_FILE} ${F_SERVICE_DB_FILE}-lock
    rm -f ${F_CONTEXT_FILE}
    for key_file in ${F_KEY_FILES[@]} ; do
        rm -f ${key_file}
    done
}

trap cleanup EXIT

# -----------------------------------------------------------------
# reset the eservice database file for the test and create the groups
# -----------------------------------------------------------------
yell create the service and groups database for host ${F_SERVICE_HOST}
try ${PDO_HOME}/bin/pdo-create-service-groups.psh  \
    --service-db ${F_SERVICE_DB_FILE} \
    --bind service_host ${F_SERVICE_HOST} \
    --bind group_file ${F_SERVICE_GROUPS_FILE}

# -----------------------------------------------------------------
# setup the contexts that will be used later for the tests
# -----------------------------------------------------------------
cd "${SOURCE_ROOT}"

rm -f ${F_CONTEXT_FILE}

yell create the context for the marbles and tokens
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/marbles.toml --bind color blue
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/marbles.toml --bind color red
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/marbles.toml --bind color green
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml --bind token test1
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml --bind token test2
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/tokens.toml --bind token test3
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/order.toml  \
           --bind order marble1 --bind user user1 \
           --bind offer_count 10 --bind offer_issuer marbles.blue.issuer \
           --bind request_count 20 --bind request_issuer marbles.green.issuer
try pdo-context load ${OPTS} --import-file ${F_CONTEXT_TEMPLATES}/order.toml \
           --bind order token1 --bind user user1 \
           --bind offer_count 1 --bind offer_issuer token.test1.token_object.token_1 \
           --bind request_count 20 --bind request_issuer marbles.green.issuer

# -----------------------------------------------------------------
# start the tests
# -----------------------------------------------------------------

# first pass, create components one at a time
yell set up the red asset type, vetting and issuer contracts
try ex_asset_type create ${OPTS} --contract marbles.red.asset_type
try ex_vetting create ${OPTS} --contract marbles.red.vetting
try ex_issuer create ${OPTS} --contract marbles.red.issuer

# finalize the approval of the issuer
yell initialize the red issuer
try ex_vetting approve_issuer ${OPTS} --contract marbles.red.vetting --issuer marbles.red.issuer
try ex_issuer initialize_issuer ${OPTS} --contract marbles.red.issuer

# and issue some assets
yell issue red assets to the users
for i in 1 2 3 4 5 ; do
    try ex_issuer issue_assets ${OPTS} --contract marbles.red.issuer \
        --owner user${i} --count "$((10 * ${i}))"
done

yell get user balances
for i in 1 2 3 4 5 ; do
    try ex_issuer balance ${OPTS} --contract marbles.red.issuer --identity user${i}
done

yell transfer assets amongst the users
for i in 1 2 3 4; do
    try ex_issuer transfer ${OPTS} --contract marbles.red.issuer --identity user${i} \
        --new-owner "user$(($i + 1))" --count "$((5 * $i))"
done

for i in 1 2 3 4 5 ; do
    try ex_issuer balance ${OPTS} --contract marbles.red.issuer --identity user${i}
done

# second pass, create "all at once"
yell create green issuer with simplified form
try ex_issuer create ${OPTS} --contract marbles.green.issuer
try ex_vetting approve_issuer ${OPTS} --contract marbles.green.vetting --issuer marbles.green.issuer
try ex_issuer initialize_issuer ${OPTS} --contract marbles.green.issuer

# and issue some assets
yell issue green assets to the users
for i in 1 2 3 4 5 ; do
    try ex_issuer issue_assets ${OPTS} --contract marbles.green.issuer \
        --owner user${i} --count "$((10 * ${i}))"
done

# second pass, create "all at once"
yell create blue issuer with simplified form
try ex_issuer create ${OPTS} --contract marbles.blue.issuer
try ex_vetting approve_issuer ${OPTS} --contract marbles.blue.vetting --issuer marbles.blue.issuer
try ex_issuer initialize_issuer ${OPTS} --contract marbles.blue.issuer

# and issue some assets
yell issue blue assets to the users
for i in 1 2 3 4 5 ; do
    try ex_issuer issue_assets ${OPTS} --contract marbles.blue.issuer \
        --owner user${i} --count "$((10 * ${i}))"
done

# run the exchange, make sure we check balances before and after
yell check balances before exchange
for color in red green blue ; do
    yell ${color} marbles
    for i in 1 2 ; do
        try ex_issuer balance ${OPTS} --contract marbles.${color}.issuer --identity user${i}
    done
done

yell create the exchange
try ex_exchange create_order ${OPTS} --contract order.marble1
try ex_exchange examine ${OPTS} --contract order.marble1
try ex_exchange match_order ${OPTS} --contract order.marble1 --identity user2
try ex_exchange claim_payment ${OPTS} --contract order.marble1
try ex_exchange claim_offer ${OPTS} --contract order.marble1 --identity user2

# run the exchange, make sure we check balances before and after
yell check balances after exchange
for color in red green blue ; do
    yell ${color} marbles
    for i in 1 2 ; do
        try ex_issuer balance ${OPTS} --contract marbles.${color}.issuer --identity user${i}
    done
done

# now run the tokens through
yell create the token issuer with a single pass
try ex_token_issuer create ${OPTS} --contract token.test1.token_issuer

yell and mint some tokens
try ex_token_object mint_tokens ${OPTS} --contract token.test1.token_object

yell transfer the tokens to the users
for i in 1 2 3 4 5 ; do
    try ex_token_object transfer ${OPTS} --contract token.test1.token_object.token_${i} \
        --new-owner "user${i}"
done

# run the exchange, make sure we check balances before and after
yell check balances before exchange
for color in red green blue ; do
    yell ${color} marbles
    for i in 1 2 3 ; do
        try ex_issuer balance ${OPTS} --contract marbles.${color}.issuer --identity user${i}
    done
done

yell create the exchange
try ex_exchange create_order ${OPTS} --contract order.token1 --verbose
try ex_exchange examine ${OPTS} --contract order.token1 --verbose
try ex_exchange match_order ${OPTS} --contract order.token1 --identity user3 --verbose
try ex_exchange claim_payment ${OPTS} --contract order.token1 --verbose
try ex_exchange claim_offer ${OPTS} --contract order.token1 --identity user3 --verbose

# run the exchange, make sure we check balances before and after
yell check balances before exchange
for color in red green blue ; do
    yell ${color} marbles
    for i in 1 2 3; do
        try ex_issuer balance ${OPTS} --contract marbles.${color}.issuer --identity user${i}
    done
done
