#!/usr/bin/env python

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

import os
import sys
import subprocess

# this should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages

## -----------------------------------------------------------------
# Versions are tied to tags on the repository; to compute correctly
# it is necessary to be within the repository itself hence the need
# to set the cwd for the bin/get_version command.
## -----------------------------------------------------------------
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
    name='pdo_digital_asset',
    version=pdo_contracts_version,
    description='Contract and support scripts for building PDO digital assets',
    author='Mic Bowman, Intel Labs',
    author_email='mic.bowman@intel.com',
    url='http://www.intel.com',
    package_dir = {
        'pdo' : 'pdo',
        'pdo.digital_asset.resources.etc' : 'etc',
        'pdo.digital_asset.resources.context' : 'context',
        'pdo.digital_asset.resources.contracts' : '../build/digital-asset-contract',
    },
    packages = [
        'pdo',
        'pdo.digital_asset',
        'pdo.digital_asset.plugins',
        'pdo.digital_asset.scripts',
        'pdo.digital_asset.resources',
        'pdo.digital_asset.resources.etc',
        'pdo.digital_asset.resources.context',
        'pdo.digital_asset.resources.contracts',
    ],
    include_package_data=True,
    install_requires = [
        'colorama',
        'pdo-client>=' + pdo_client_version,
        'pdo-common-library>=' + pdo_client_version,
        'pdo-sservice>=' + pdo_client_version,
        'pdo-exchange>=' + pdo_contracts_version,
    ],
    entry_points = {
        'console_scripts' : [
            'da_token=pdo.digital_asset.scripts.scripts:da_token',
            'da_guardian=pdo.digital_asset.scripts.scripts:da_guardian',
        ]
    }
)
