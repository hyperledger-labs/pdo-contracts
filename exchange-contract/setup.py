#!/usr/bin/env python

# Copyright 2018 Intel Corporation
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
    name='pdo_exchange',
    version=pdo_contracts_version,
    description='Support functions PDO exchange contracts',
    author='Mic Bowman, Intel Labs',
    author_email='mic.bowman@intel.com',
    url='http://www.intel.com',
    package_dir = {
        'pdo' : 'pdo',
        'pdo.exchange.resources.etc' : 'etc',
        'pdo.exchange.resources.context' : 'context',
        'pdo.exchange.resources.contracts' : '../build/exchange-contract',
        'pdo.exchange.resources.scripts' : 'scripts',
    },
    packages = [
        'pdo',
        'pdo.contracts',
        'pdo.exchange',
        'pdo.exchange.plugins',
        'pdo.exchange.scripts',
        'pdo.exchange.resources',
        'pdo.exchange.resources.etc',
        'pdo.exchange.resources.context',
        'pdo.exchange.resources.contracts',
        'pdo.exchange.resources.scripts',
    ],
    include_package_data=True,
    install_requires = [
        'colorama',
        'pdo-client>=' + pdo_client_version,
        'pdo-common-library>=' + pdo_client_version,
        'pdo-sservice>=' + pdo_client_version,
    ],
    entry_points = {
        'console_scripts' : [
            'ex_asset_type=pdo.exchange.scripts.scripts:asset_type',
            'ex_vetting=pdo.exchange.scripts.scripts:vetting',
            'ex_issuer=pdo.exchange.scripts.scripts:issuer',
            'ex_guardian=pdo.exchange.scripts.scripts:guardian',
            'ex_token_issuer=pdo.exchange.scripts.scripts:token_issuer',
            'ex_token_object=pdo.exchange.scripts.scripts:token_object',
            'ex_exchange=pdo.exchange.scripts.scripts:exchange',
        ]
    }
)
