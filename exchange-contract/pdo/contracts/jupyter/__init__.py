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

import importlib.util

import IPython.display as ip_display

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.context as pcontext
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell

import pdo.client.commands.context as pcontext_cmd
import pdo.client.commands.contract as pcontract_cmd
import pdo.client.commands.collection as pcollection_cmd

import pdo.contracts.common as common
import pdo.contracts.jupyter.groups as groups
import pdo.contracts.jupyter.keys as keys
import pdo.contracts.jupyter.services as services
import pdo.contracts.jupyter.common_widgets as widgets

from .utility import *

# -----------------------------------------------------------------
# Load plugins from the contract families. Each contract family
# is listed (the python module for it) with a short, unique prefix
# that will be prepended to each of the module names. This way all
# of the contract family plugins can be made available easily through
# the single jupyter module. for example, ex_asset_type will provide
# access to the exchange family asset type plugin module.
# -----------------------------------------------------------------
_contract_families_ = {
    'exchange' : 'ex',
    'inference' : 'ml',
}

for cf, cs in _contract_families_.items() :
    try :
        # attempt to load the jupyter module from the contract family
        # not a problem if this fails
        jupyter_name = 'pdo.{}.jupyter'.format(cf)
        jupyter_module = importlib.import_module(jupyter_name)
        globals()['{}_jupyter'.format(cs)] = jupyter_module
    except Exception as e :
        raise ImportError('Failed to import module for contract family {}; {}'.format(cf, e))

    # load the plugins module for the contract family, this
    # should provide a list of all the plugins in the family
    # (in the __all__ variable)
    try :
        family_name = 'pdo.{}.plugins'.format(cf)
        family_module = importlib.import_module(family_name)

        for plugin_name in family_module.__all__ :
            plugin_module = importlib.import_module('{}.{}'.format(family_name, plugin_name))
            globals()['{}_{}'.format(cs, plugin_name)] = plugin_module
    except Exception as e :
        raise ImportError('Failed to import plugins module for contract family {}; {}'.format(cf, e))
