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


import copy
import logging
import sys
import types

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.context as pcontext
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell

import pdo.client.commands.context as pcontext_cmd
import pdo.client.commands.contract as pcontract_cmd

import pdo.exchange.plugins.asset_type as ex_asset_type
import pdo.exchange.plugins.exchange as ex_exchange
import pdo.exchange.plugins.guardian as ex_guardian
import pdo.exchange.plugins.issuer as ex_issuer
import pdo.exchange.plugins.token_issuer as ex_token_issuer
import pdo.exchange.plugins.token_object as ex_token_object
import pdo.exchange.plugins.vetting as ex_vetting

logger = logging.getLogger(__name__)

logging.getLogger('papermill.translators').setLevel(logging.ERROR)

# -----------------------------------------------------------------
# Code based on suggestions found here:
# https://stackoverflow.com/questions/26494747/simple-way-to-choose-which-cells-to-run-in-ipython-notebook-during-run-all
#
# Enable by adding this to the top of the notebook:
# load_ipython_extension(get_ipython())
#
# Add to cell as:
# %%skip True
# %%skip False
# %%skip <any python expression>
# -----------------------------------------------------------------
def skip(line, cell=None) :
    """Skip execution of the current line/cell if line evaluates to True.
    """
    if eval(line):
        return

    get_ipython().run_cell(cell)

def load_ipython_extension(shell):
    """Registers the skip magic when the extension loads.
    """
    shell.register_magic_function(skip, 'line_cell')

def unload_ipython_extension(shell):
    """Unregister the skip magic when the extension unloads.
    """
    del shell.magics_manager.magics['cell']['skip']

# -----------------------------------------------------------------
# set up the general configuration
# -----------------------------------------------------------------
__default_configuration__ = {
    'bind' : [],
    'ledger' : None,                      # URL for the ledger
    'data_dir' : None,                    # directory where data will be read/saved
    'source_dir' : [],                    # directories to search for contract files
    'key_dir' : [],                       # directories to search for key files
    'service_db' : None,                  # name of the enclave service database
    'service_groups' : [],                # list of service group files
    'config' : [],                        # list of configuration files
    'client_identity' : None,             # initial identity
    'client_key_file' : None,             # key file associated with the identity
    'verbose' : True,                     # interactive output verbosity
    'logfile' : '__screen__',
    'loglevel' : None,
}

configuration = types.SimpleNamespace(**__default_configuration__)

def initialize_environment(identity, **kwargs) :
    global configuration

    configuration.client_identity = identity
    configuration.client_key_file = '{}_private.pem'.format(identity)

    # the simple version of this list(kwargs.items()) seems to generate an
    # extra level of list when put into a namespace object
    for (k, v) in kwargs.items() :
        configuration.bind += [(k, v)]

    environment = pshell.initialize_environment(configuration)
    if environment is None :
        raise Exception('failed to initialize the environment')

    return environment

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
asset_type_context = {
    'module' : 'pdo.exchange.plugins.asset_type',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.asset_type.source}',
    'name' : 'asset_type',
    'description' : 'asset type',
    'link' : 'http://',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

vetting_context = {
    'module' : 'pdo.exchange.plugins.vetting',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.vetting.source}',
    'asset_type_context' : '@{..asset_type}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

issuer_context = {
    'module' : 'pdo.exchange.plugins.issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.issuer.source}',
    'asset_type_context' : '@{..asset_type}',
    'vetting_context' : '@{..vetting}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

guardian_context = {
    'module' : 'pdo.exchange.plugins.guardian',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.data_guardian.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

token_issuer_context = {
    'module' : 'pdo.exchange.plugins.token_issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.token_issuer.source}',
    'token_object_context' : '@{..token_object}',
    'vetting_context' : '@{..vetting}',
    'guardian_context' : '@{..guardian}',
    'description' : 'issuer for token',
    'token_metadata' : {
        'opaque' : '',
    },
    'count' : 10,
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

token_object_context = {
    'module' : 'pdo.exchange.plugins.token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

order_context = {
    'module' : 'pdo.exchange.plugins.exchange',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.exchange.source}',
    'offer' : {
        'issuer_context' : '@{context.${offer_issuer}}',
        'count' : 1,
    },
    'request' : {
        'issuer_context' : '@{context.${request_issuer}}',
        'count' : 1,
    },
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

context_map = {
    'asset_type' : asset_type_context,
    'vetting' : vetting_context,
    'issuer' : issuer_context,
    'guardian' : guardian_context,
    'token_issuer' : token_issuer_context,
    'token_object' : token_object_context,
    'order' : order_context,
}

# -----------------------------------------------------------------
# initialize_context
# -----------------------------------------------------------------
def initialize_context(state, bindings, context_file, prefix, contexts, **kwargs) :
    """Load context from a file and instantiate context templates
    """

    # attempt to load the context from the context file
    try :
        pbuilder.Context.LoadContextFile(state, bindings, context_file)
    except :
        logger.warning('failed to load context from {}'.format(context_file))

    context =  pbuilder.Context(state, prefix)
    if context.has_key('initialized') :
        return context

    for c in contexts :
        context.set(c, copy.deepcopy(context_map[c]))

    for (k, v) in kwargs.items() :
        context.set(k, v)

    context.set('initialized', True)
    return context

def initialize_asset_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['asset_type', 'vetting', 'issuer']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_token_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_order_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['order']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
