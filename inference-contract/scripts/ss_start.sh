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

source ${PDO_HOME}/bin/lib/common.sh

check_python_version

F_SERVICE_NAME=guardian_sservice
F_SERVICE_CMD=${PDO_INSTALL_ROOT}/bin/sservice

# -----------------------------------------------------------------
# Process command line arguments
# -----------------------------------------------------------------
F_SCRIPT_NAME=$(basename ${BASH_SOURCE[-1]} )

F_CLEAN='no'
F_OUTPUTDIR=''

F_USAGE='-c|--clean -o|--output dir --help -- <service options>'
F_SHORT_OPTS='co:'
F_LONG_OPTS='clean,output:,help'

TEMP=$(getopt -o ${F_SHORT_OPTS} --long ${F_LONG_OPTS} -n "${F_SCRIPT_NAME}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${F_SCRIPT_NAME} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -c|--clean) F_CLEAN="yes" ; shift 1 ;;
        -o|--output) F_OUTPUTDIR="$2" ; shift 2 ;;
        --help) echo "Usage: ${SCRIPT_NAME} ${F_USAGE}"; exit 0 ;;
    	--) shift ; break ;;
    	*) echo "Internal error!" ; exit 1 ;;
    esac
done

# do not start if the service is already running
PLIST=$(pgrep -f ${F_SERVICE_CMD})
if [ -n "$PLIST" ] ; then
    echo existing storage service detected, please shutdown first
    exit 1
fi

# start service asynchronously
echo start ${F_SERVICE_NAME}

if [ "${F_CLEAN}" == "yes" ]; then
    rm -f ${PDO_HOME}/logs/${F_SERVICE_NAME}.log
    rm -f ${PDO_HOME}/logs/${F_SERVICE_NAME}.log
fi

rm -f ${PDO_HOME}/logs/${F_SERVICE_NAME}.pid

if [ "${F_OUTPUTDIR}" != "" ]  ; then
    EFILE="${F_OUTPUTDIR}/${F_SERVICE_NAME}.err"
    OFILE="${F_OUTPUTDIR}/${F_SERVICE_NAME}.out"
    rm -f $EFILE $OFILE
else
    EFILE=/dev/null
    OFILE=/dev/null
fi

${F_SERVICE_CMD} $@ 2> $EFILE > $OFILE &
echo $! > ${PDO_HOME}/logs/${F_SERVICE_NAME}.pid
