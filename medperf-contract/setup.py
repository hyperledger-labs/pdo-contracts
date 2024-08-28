#!/usr/bin/env python

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

import os
import sys
import subprocess
import warnings

# this should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages, find_namespace_packages

# -----------------------------------------------------------------
# Versions are tied to tags on the repository; to compute correctly
# it is necessary to be within the repository itself hence the need
# to set the cwd for the bin/get_version command.
# -----------------------------------------------------------------
root_dir = os.path.dirname(os.path.realpath(__file__))
try :
    pdo_contracts_version = subprocess.check_output(
        'bin/get_version', cwd=os.path.join(root_dir, os.pardir)).decode('ascii').strip()
except Exception as e :
    warnings.warn('Failed to get pdo_contracts version, using the default')
    pdo_contracts_version = '0.0.0'

try :
    pdo_client_version = subprocess.check_output(
        'bin/get_version', cwd=os.path.join(root_dir, os.pardir, 'private-data-objects')).decode('ascii').strip()
except Exception as e :
    warnings.warn('Failed to get pdo_client version, using the default')
    pdo_client_version = '0.0.0'

## -----------------------------------------------------------------
## -----------------------------------------------------------------
setup(
    name='pdo_medperf',
    version=pdo_contracts_version,
    description='Implementation of guardian service for MedPerf experiment execution',
    author='Wenyi Tang, Intel Labs',
    author_email='wenyi1.tang@intel.com',
    url='http://www.intel.com',
    package_dir = {
        'pdo' : 'pdo',
        'pdo.medperf.resources.etc' : 'etc',
        'pdo.medperf.resources.context' : 'context',
        'pdo.medperf.resources.contracts' : '../build/medperf-contract',
        'pdo.medperf.resources.scripts' : 'scripts',
    },
    packages = [
        'pdo',
        'pdo.medperf',
        'pdo.medperf.plugins',
        'pdo.medperf.scripts',
        'pdo.medperf.common',
        'pdo.medperf.operations',
        'pdo.medperf.wsgi',
        'pdo.medperf.resources',
        'pdo.medperf.resources.etc',
        'pdo.medperf.resources.context',
        'pdo.medperf.resources.contracts',
        'pdo.medperf.resources.scripts',
    ],
    include_package_data=True,
    # add everything from requirements.txt here
    install_requires = [
        'colorama',
        'colorlog',
        'lmdb',
        'toml',
        'twisted',
        'jsonschema>=3.0.1',
        'requests',
        'urllib3',
        'pdo-client>=' + pdo_client_version,
        'pdo-common-library>=' + pdo_client_version,
        'pdo-sservice>=' + pdo_client_version,
        'pdo-exchange>=' + pdo_contracts_version,
    ],
    entry_points = {
        'console_scripts' : [
           'medperf_token=pdo.medperf.scripts.scripts:medperf_token',
           'medperf_guardian_service=pdo.medperf.scripts.guardianCLI:Main',
        ]
    }
)
