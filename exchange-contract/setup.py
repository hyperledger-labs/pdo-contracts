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

# this should only be run with python3
import sys
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup, find_packages, find_namespace_packages

# -----------------------------------------------------------------
# -----------------------------------------------------------------
root_dir = os.path.dirname(os.path.realpath(__file__))
# version = subprocess.check_output(
#     os.path.join(root_dir, 'bin/get_version')).decode('ascii').strip()
version = '0.0.0'

## -----------------------------------------------------------------
## -----------------------------------------------------------------
setup(
    name='pdo_exchange',
    version=version,
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
        'pdo-client>=0.2.49',
        'pdo-common-library>=0.2.49',
        'pdo-sservice>=0.2.49',
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
