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

F_SERVICE_NAME=medperf_guardian_service
F_SERVICE_CMD=${PDO_INSTALL_ROOT}/bin/${F_SERVICE_NAME}

if [ -f ${PDO_HOME}/logs/${F_SERVICE_NAME}.pid ]; then
    F_PID=$(cat ${PDO_HOME}/logs/${F_SERVICE_NAME}.pid)
else
    yell unable to locate service pid file

    F_PID=$(pgrep -f "${F_SERVICE_CMD}")
    if [ ! -n "${F_PID}" ] ; then
        yell unable to locate service process
        exit
    fi
fi

try ps -h --format pid,start,cmd -p $F_PID
