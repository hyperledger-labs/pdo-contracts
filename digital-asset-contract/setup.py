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
## -----------------------------------------------------------------
root_dir = os.path.dirname(os.path.realpath(__file__))
# version = subprocess.check_output(
#     os.path.join(root_dir, 'bin/get_version')).decode('ascii').strip()
version = '0.0.0'

## -----------------------------------------------------------------
## -----------------------------------------------------------------
setup(
    name='pdo_digital_asset',
    version=version,
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
        'pdo-client>=0.2.49',
        'pdo-common-library>=0.2.49',
        'pdo-sservice>=0.2.49',
        'pdo-exchange',
    ],
    entry_points = {
        'console_scripts' : [
            'da_token=pdo.digital_asset.scripts.scripts:da_token',
            'da_guardian=pdo.digital_asset.scripts.scripts:da_guardian',
        ]
    }
)
