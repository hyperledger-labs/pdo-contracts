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

from pdo.client.builder.shell import run_shell_command

import warnings
warnings.catch_warnings()
warnings.simplefilter("ignore")

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def asset_type() :
    run_shell_command('do_asset_type', 'pdo.exchange.plugins.asset_type')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def vetting() :
    run_shell_command('do_vetting', 'pdo.exchange.plugins.vetting')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def issuer() :
    run_shell_command('do_issuer', 'pdo.exchange.plugins.issuer')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def guardian() :
    run_shell_command('do_guardian', 'pdo.exchange.plugins.guardin')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def token_issuer() :
    run_shell_command('do_token_issuer', 'pdo.exchange.plugins.token_issuer')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def token_object() :
    run_shell_command('do_token_object', 'pdo.exchange.plugins.token_object')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def exchange() :
    run_shell_command('do_exchange', 'pdo.exchange.plugins.exchange')
