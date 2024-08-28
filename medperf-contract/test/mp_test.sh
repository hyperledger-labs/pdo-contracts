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

# -----------------------------------------------------------------
# -----------------------------------------------------------------
: "${PDO_LEDGER_URL?Missing environment variable PDO_LEDGER_URL}"
: "${PDO_HOME?Missing environment variable PDO_HOME}"
: "${PDO_SOURCE_ROOT?Missing environment variable PDO_SOURCE_ROOT}"
: "${MEDPERF_SQLITE_PATH?Missing environment variable MEDPERF_SQLITE_PATH}"
: "${MEDPERF_VENV_PATH?Missing environment variable MEDPERF_VENV_PATH}"
: "${MEDPERF_HOME?Missing environment variable MEDPERF_HOME}"
# -----------------------------------------------------------------
# -----------------------------------------------------------------
source ${PDO_HOME}/bin/lib/common.sh
check_python_version

# note
# ./script_test.sh --host 10.54.66.43 --ledger http://10.54.66.43:6600

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
F_GUARDIAN_HOST=10.54.66.42
F_LEDGER_URL=${PDO_LEDGER_URL}
F_LOGLEVEL=${PDO_LOG_LEVEL:-info}
F_LOGFILE=${PDO_LOG_FILE:-__screen__}
F_CONTEXT_FILE=${SOURCE_ROOT}/test/test_context.toml
F_CONTEXT_TEMPLATES=${PDO_HOME}/contracts/medperf/context
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
    ${PDO_HOME}/contracts/medperf/scripts/gs_stop.sh
    ${PDO_HOME}/contracts/medperf/scripts/ss_stop.sh
}

trap cleanup EXIT

# -----------------------------------------------------------------
# Start the guardian service and the storage service
# -----------------------------------------------------------------
try ${PDO_HOME}/contracts/medperf/scripts/ss_start.sh -c -o ${PDO_HOME}/logs -- \
    --loglevel debug \
    --config guardian_service.toml \
    --config-dir ${PDO_HOME}/etc/contracts \
    --identity guardian_sservice

sleep 3

try ${PDO_HOME}/contracts/medperf/scripts/gs_start.sh -c -o ${PDO_HOME}/logs -- \
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


yell ===========================================================================
yell Start the tests for PDO and MedPerf
yell ===========================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
RESET='\033[0m'

read -p "Press enter to continue >>"

echo -e "${GREEN}===========================${RESET}"
echo -e "${GREEN}=== Preparing MedPerf ===${RESET}"
echo -e "${GREEN}===========================${RESET}"

deactivate

source $MEDPERF_VENV_PATH'/bin/activate'
cd ${MEDPERF_HOME}
rm -fr medperf_tutorial
cd server
sh reset_db.sh
rm -fr ~/.medperf/localhost_8000
python seed.py --demo data
cd ..
sh tutorials_scripts/setup_data_tutorial.sh

medperf dataset submit \
  --name "mytestdata" \
  --description "A tutorial dataset" \
  --location "My machine" \
  --data_path "medperf_tutorial/sample_raw_data/images" \
  --labels_path "medperf_tutorial/sample_raw_data/labels" \
  --benchmark 1



medperf dataset prepare --data_uid 1
echo -e "${GREEN}Putting some dummy models assosciated with experiment..."
read -p "Press enter to continue >>"
python record_writer/fake_model.py
# clear

echo -e "${YELLOW}======================================================${RESET}"
echo -e "${YELLOW}The next commmand will set the dataset as operational.${RESET}"
echo -e "${YELLOW}This is a good time to mint a token for the dataset.${RESET}"
echo -e "${YELLOW}======================================================${RESET}"
read -p "Press enter to continue >>"

medperf dataset set_operational --data_uid 1

deactivate
source ${PDO_INSTALL_ROOT}'/bin/activate'

# mint token here
yell create a token issuer and mint the tokens. This token does not have any policy
try ex_token_issuer create ${OPTS} --contract token.test1.token_issuer
try medperf_token mint_dataset_tokens ${OPTS} --contract token.test1.token_object \
    --dataset_id "mytestdata" 


deactivate
source $MEDPERF_VENV_PATH'/bin/activate'

clear

echo -e "${YELLOW}=======================================================================${RESET}"
echo -e "${YELLOW}The next command will associate the dataset with experiment.${RESET}"
echo -e "${YELLOW}This is a good time to update the token policy for the dataset.${RESET}"
echo -e "${YELLOW}The experiment is associated with 10 models marked from 1-10 ${RESET}"
echo -e "${YELLOW}The policy specifies the dataowner only allows 3 models to be evaluated${RESET}"
echo -e "${YELLOW}========================================================================${RESET}"
read -p "Press enter to continue >>"

medperf dataset associate --benchmark_uid 1 --data_uid 1 > /dev/null

deactivate
source ${PDO_INSTALL_ROOT}'/bin/activate'

# update token policy here
yell the owner of the dataset token updates the policy by adding an experiment id and a list of associated models
yell the experiment contains 10 models, but the dataset can be used only 3 times
try medperf_token update_policy ${OPTS}  --contract token.test1.token_object.token_1 \
    --dataset_id "mytestdata" \
    --experiment_id "chestxray" \
    --associated_model_ids "10" \
    --max_use_count 3

# check token policy here
# yell get dataset and policy info from the token object
# try medperf_token get_dataset_info ${OPTS} --contract token.test1.token_object.token_1 \

# clear

echo -e "${YELLOW}============================================================${RESET}"
echo -e "${YELLOW}The dataowner can transfer the token to experiment committee${RESET}"
echo -e "${YELLOW}============================================================${RESET}"
read -p "Press enter to continue >>"

# transfer token here
yell the owner transfers the token to token_holder1 '(experiment committee)'
try medperf_token transfer ${OPTS} --contract token.test1.token_object.token_1 \
    --new-owner token_holder1

# echo -e "${YELLOW} Update policy is not allowed from the experiment committee${RESET}"
# update token policy here
yell the experiment committee tries to update the policy to a maximum 10 uese, but fails
medperf_token update_policy ${OPTS}  --contract token.test1.token_object.token_1 \
    --experiment_id "chestxray" \
    --dataset_id "mytestdata" \
    --associated_model_ids "10" \
    --max_use_count 10 \
    --identity token_holder1

# echo -e "${YELLOW} Update policy is not allowed from the experiment committee${RESET}"
# yell the token_issuer tries to update the policy to a maximum 2 uses
# try medperf_token update_policy ${OPTS}  --contract token.test1.token_object.token_1 \
#     --experiment_id "chestxray" \
#     --dataset_id "mytestdata" \
#     --associated_model_ids "10" \
#     --max_use_count 2 

# yell Check the new policy
# try medperf_token get_dataset_info ${OPTS} --contract token.test1.token_object.token_1 \
#     --identity token_holder1


# clear
echo -e "${YELLOW}============================================================${RESET}"
echo -e "${YELLOW} Experiment committee can choose which models to use.${RESET}"
echo -e "${YELLOW} These models are marked scheduled in PDO contract. ${RESET}"
echo -e "${YELLOW}============================================================${RESET}"
# read -p "Press enter to continue >>"

yell Try to use model 3, it works
medperf_token use_dataset ${OPTS}  --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --model_ids_to_evaluate '3'
# out of range not allowed

# read -p "Press enter to continue >>"
yell Try use a model 15 that is not associated with the experiment, but fails
medperf_token use_dataset ${OPTS}  --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --model_ids_to_evaluate '15'

# two
# read -p "Press enter to continue >>"
yell Try to use model 4, it works
try medperf_token use_dataset ${OPTS}  --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --model_ids_to_evaluate '4'

yell Try to use model 5, it works
try medperf_token use_dataset ${OPTS}  --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --model_ids_to_evaluate '5'

# three not allowed 
# read -p "Press enter to continue >>"
yell Try to use model 6, it fails because the maximum use count is 3
try medperf_token use_dataset ${OPTS}  --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --model_ids_to_evaluate '6'

# read -p "Press enter to continue >>"
# yell check the token policy status again
# try medperf_token get_dataset_info ${OPTS} --contract token.test1.token_object.token_1 \
#     --identity token_holder1

read -p "Press enter to continue >>"
# clear
echo -e "${YELLOW}============================================================${RESET}"
echo -e "${YELLOW}The experiment committee can pack all scheduled models into ${RESET}"
echo -e "${YELLOW}a single experiment workorder send it to the medperf server.${RESET}"
echo -e "${YELLOW}============================================================${RESET}"
read -p "Press enter to continue >>"

yell Experiment Committee gets a packed workorder and submit to the MedPerf server
medperf_token experiment_order ${OPTS} --contract token.test1.token_object.token_1 \
    --identity token_holder1 \
    --dataset_id "mytestdata" \
    --medperf_sqlite_path



yell Check the token policy status again
try medperf_token get_dataset_info ${OPTS} --contract token.test1.token_object.token_1 \
    --identity token_holder1

read -p "Press enter to check the results >>"

echo -e "${YELLOW}============================================================${RESET}"
echo -e "${YELLOW}The results of the experiment look like this.${RESET}"
echo -e "${YELLOW}============================================================${RESET}"
# 
for i in {3,4,5};
do
    # echo -e "${YELLOW}============================================================${RESET}"
    echo -e "${YELLOW}Model $i${RESET}"
    # echo -e "${YELLOW}============================================================${RESET}"
    cat $MEDPERF_HOME/test_resource/test_results/$i*
done
read -p "Press enter to quit"

exit

