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
import warnings

## -----------------------------------------------------------------
# Change values of the following variables to customize your
# contract family; the contract_scripts variable is a list of
# bash commands that will be created in the python wheel. See
# ./pdo/{contract_family}/scripts/scripts.py for more information
# on building command line scripts.
## -----------------------------------------------------------------
contract_family = 'example'
contract_scripts = [ 'example_counter' ]

author = 'Mic Bowman, Intel Labs'
author_email = 'mic.bowman@intel.com'
author_url = 'http://www.intel.com'

## -----------------------------------------------------------------
# Unless you change the standard behavior or layout of the contract
# there should be no changes required below
## -----------------------------------------------------------------

# this should only be run with python3
if sys.version_info[0] < 3:
    print('ERROR: must run with python3')
    sys.exit(1)

from setuptools import setup

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
    warnings.warn(f'Failed to get pdo_contracts version, using the default; {e}')
    pdo_contracts_version = '0.0.0'

try :
    pdo_client_version = subprocess.check_output(
        'bin/get_version', cwd=os.path.join(root_dir, os.pardir, 'private-data-objects')).decode('ascii').strip()
except Exception as e :
    warnings.warn(f'Failed to get pdo_client version, using the default; {e}')
    pdo_client_version = '0.0.0'

## -----------------------------------------------------------------
## -----------------------------------------------------------------
setup(
    name=f'pdo_{contract_family}',
    version=pdo_contracts_version,
    description='Contract and support scripts for a PDO contract',
    author=author,
    author_email=author_email,
    url=author_url,
    package_dir = {
        'pdo' : 'pdo',
        f'pdo.{contract_family}.resources.etc' : 'etc',
        f'pdo.{contract_family}.resources.context' : 'context',
        f'pdo.{contract_family}.resources.contracts' : f'../build/{contract_family}-contract',
    },
    packages = [
        'pdo',
        f'pdo.{contract_family}',
        f'pdo.{contract_family}.jupyter',
        f'pdo.{contract_family}.plugins',
        f'pdo.{contract_family}.scripts',
        f'pdo.{contract_family}.resources',
        f'pdo.{contract_family}.resources.etc',
        f'pdo.{contract_family}.resources.context',
        f'pdo.{contract_family}.resources.contracts',
    ],
    include_package_data=True,
    install_requires = [
        'colorama',
        'pdo-client>=' + pdo_client_version,
        'pdo-common-library>=' + pdo_client_version,
    ],
    entry_points = {
        'console_scripts' : list(map(lambda s : f'{s}=pdo.{contract_family}.scripts.scripts:{s}', contract_scripts)),
    }
)
