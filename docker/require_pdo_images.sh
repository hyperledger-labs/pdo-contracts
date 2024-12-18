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

SCRIPT_NAME=$(basename ${BASH_SOURCE[-1]} )
source ${PDO_HOME}/bin/lib/common.sh

# -----------------------------------------------------------------
# Process command line arguments
# -----------------------------------------------------------------
F_REGISTRY=
F_VERSION=latest

F_USAGE='-r|--registry [registry] -v|--version [pdo_version]'
SHORT_OPTS='r:v:'
LONG_OPTS='registry:,version:'

TEMP=$(getopt -o ${SHORT_OPTS} --long ${LONG_OPTS} -n "${SCRIPT_NAME}" -- "$@")
if [ $? != 0 ] ; then echo "Usage: ${SCRIPT_NAME} ${F_USAGE}" >&2 ; exit 1 ; fi

eval set -- "$TEMP"
while true ; do
    case "$1" in
        -r|--registry) F_REGISTRY="$2" ; shift 2 ;;
        -v|--version) F_VERSION="$2" ; shift 2 ;;
        --help) echo "Usage: ${SCRIPT_NAME} ${F_USAGE}"; exit 0 ;;
    	--) shift ; break ;;
    	*) echo "Internal error!" ; exit 1 ;;
    esac
done

# if a registry is specified then make sure it has a trailing '/'
if [ -n "${F_REGISTRY}" ]; then
   if [[ "${F_REGISTRY}" != */ ]]; then
       F_REGISTRY=${F_REGISTRY}/
   fi
fi

# check for each of the PDO images
for image in pdo_ccf pdo_services pdo_client ; do
    # First check to see if there is a local version that matches
    if docker inspect ${F_REGISTRY}$image:${F_VERSION} > /dev/null 2>&1 ; then
        continue
    fi

    # Pull the image if there is a registry and fail if not
    yell Attempt to pull ${F_REGISTRY}$image:${F_VERSION}
    docker pull ${F_REGISTRY}$image:${F_VERSION} > /dev/null 2>&1 || \
        die Unable to find ${F_REGISTRY}$image:${F_VERSION}
done

exit 0
