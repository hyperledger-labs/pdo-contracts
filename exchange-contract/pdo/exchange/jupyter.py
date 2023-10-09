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
import os
import random
import string
import sys
import toml
import types
import typing

from zipfile import ZipFile
from tempfile import TemporaryDirectory

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

_logger = logging.getLogger(__name__)

logging.getLogger('papermill.translators').setLevel(logging.ERROR)

# -----------------------------------------------------------------
# Code based on suggestions found here:
# https://stackoverflow.com/questions/26494747/simple-way-to-choose-which-cells-to-run-in-ipython-notebook-during-run-all
# -----------------------------------------------------------------
def skip(line, cell=None) :
    """Skip execution of the current line/cell if line evaluates to True.

    Enable by adding this to the top of the notebook::
        load_ipython_extension(get_ipython())

    Add to cell as::
        %%skip True
        %%skip False
        %%skip <any python expression>
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
_default_configuration_ = {
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

def initialize_environment(identity : str, **kwargs) :
    """Initialize the PDO client environment

    This function is similar to others that parse command line
    parameters to configure the PDO client. However, the values
    come from a dictionary, rather than the command line.

    @param identity: short form of the identity
    @keyword kwargs: configuration and binding parameters
    @rtype: tuple[pdo.client.builder.state.State, pdo.client.builder.bindings.Bindings]
    @return: a PDO client environment or None if configuration failed
    """
    configuration = types.SimpleNamespace(**_default_configuration_)
    configuration.client_identity = identity
    configuration.client_key_file = '{}_private.pem'.format(identity)

    # the simple version of this list(kwargs.items()) seems to generate an
    # extra level of list when put into a namespace object
    configuration.bind = []
    for (k, v) in kwargs.items() :
        if k in _default_configuration_ :
            configuration.__setattr__(k, v)
        else :
            configuration.bind += [(k, v)]

    environment = pshell.initialize_environment(configuration)
    if environment is None :
        raise Exception('failed to initialize the environment')

    return environment

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
_asset_type_context_ = {
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

_vetting_context_ = {
    'module' : 'pdo.exchange.plugins.vetting',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.vetting.source}',
    'asset_type_context' : '@{..asset_type}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_issuer_context_ = {
    'module' : 'pdo.exchange.plugins.issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.issuer.source}',
    'asset_type_context' : '@{..asset_type}',
    'vetting_context' : '@{..vetting}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_guardian_context_ = {
    'module' : 'pdo.exchange.plugins.guardian',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.data_guardian.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_token_issuer_context_ = {
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

_token_object_context_ = {
    'module' : 'pdo.exchange.plugins.token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_order_context_ = {
    'module' : 'pdo.exchange.plugins.exchange',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.exchange.source}',
    'offer' : {
        'issuer_context' : '@{...offer.issuer}',
        'count' : 1,
    },
    'request' : {
        'issuer_context' : '@{...request.issuer}',
        'count' : 1,
    },
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_context_map_ = {
    'asset_type' : _asset_type_context_,
    'vetting' : _vetting_context_,
    'issuer' : _issuer_context_,
    'guardian' : _guardian_context_,
    'token_issuer' : _token_issuer_context_,
    'token_object' : _token_object_context_,
    'order' : _order_context_,
}

# -----------------------------------------------------------------
# initialize_context
# -----------------------------------------------------------------
def _initialize_context_(state, bindings, context_file : str, prefix : str, contexts : typing.List[str], **kwargs) :
    # attempt to load the context from the context file
    try :
        pbuilder.Context.LoadContextFile(state, bindings, context_file, prefix=prefix)
    except :
        _logger.warning('failed to load context from {}'.format(context_file))

    context =  pbuilder.Context(state, prefix)
    if not context.has_key('initialized') :
        for c in contexts :
            context.set(c, copy.deepcopy(_context_map_[c]))

        context.set('initialized', True)

    # even if the context is initialized, override the bindings
    # this is useful for personalizing a context for a contract
    # that already exists (like using a different identity)
    for (k, v) in kwargs.items() :
        context.set(k, v)

    return context

def initialize_asset_context(state, bindings, context_file : str, prefix : str, **kwargs) :
    """Initialize a context for issuing assets

    The context is create from asset type, vetting and issuer contexts.

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @param context_file: name of the context file
    @param prefix: prefix for paths in the context
    @keyword kwargs: dictionary of string (paths) to values that override context
    @rtype: pdo.client.builder.context.Context
    @return: the initialized context
    """
    contexts = ['asset_type', 'vetting', 'issuer']
    return _initialize_context_(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_token_context(state, bindings, context_file : str, prefix : str, **kwargs) :
    """Initialize a context for minting tokens

    The context is create from asset type, vetting, guardian,
    token_issuer and token_object contexts.

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @param context_file: name of the context file
    @param prefix: prefix for paths in the context
    @keyword kwargs: dictionary of string (paths) to values that override context
    @rtype: pdo.client.builder.context.Context
    @return: the initialized context
    """
    contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
    return _initialize_context_(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_order_context(state, bindings, context_file, prefix, **kwargs) :
    """Initialize a context for creating an order to exchange assets

    The context is create from order context.

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @param context_file: name of the context file
    @param prefix: prefix for paths in the context
    @keyword kwargs: dictionary of string (paths) to values that override context
    @rtype: pdo.client.builder.context.Context
    @return: the initialized context
    """
    contexts = ['order']
    return _initialize_context_(state, bindings, context_file, prefix, contexts, **kwargs)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def export_context_file(state, bindings, context, contexts : typing.List[str], export_file : str) :
    """Export the context and associated contract files to a zip file that
    can be shared with others who want to use the contract

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @type context: pdo.client.builder.context.Context
    @param context: current context
    @param contexts : list of path expressions to retrieve values from a context
    @param export_file : name of the file where the contract family will be written
    """

    # the context we create is initialized, mark it so
    export_context = {
        'contexts' : contexts,
        'initialized' : True,
    }

    save_files = []

    # while there are fields in the context that are unnecessary for
    # future use of the contract, it is far easier to simply copy them
    # here. at some point, this may be smarter about only copying the
    # fields that are necessary.
    for c in contexts :
        # since the incoming contexts are paths, we need to make sure
        # we copy the context from/to the right location
        (*prefix, key) = c.split('.')
        ec = export_context
        for p in prefix :
            if p not in ec :
                ec[p] = {}
            ec = ec[p]
        ec[key] = copy.deepcopy(context.get(c))
        save_files.append(context.get('{}.save_file'.format(c)))

    data_directory = state.get(['Contract', 'DataDirectory'], bindings['data'])

    with ZipFile(bindings.expand(export_file), 'w') as zf :
        # add the context to the package, this has a canonical name
        zf.writestr('context.toml', toml.dumps(export_context))

        # add the contract save files to the package
        for s in save_files :
            contract_file_name = os.path.join(data_directory, '__contract_cache__', s)
            zf.write(contract_file_name, arcname=s)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def import_context_file(state, bindings, context_file_name : str, import_file : str) :
    """Extract the context and contract files from a contract import file

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @param context_file_name : name of the file to save imported context
    @param import_file : name of the contract family file to import
    @rtype: pdo.client.builder.context.Context
    @return: the initialized context
    """

    with ZipFile(bindings.expand(import_file), 'r') as zf :
        # extract the context file from the package and save it
        # in the specified file
        context = toml.loads(zf.read('context.toml').decode())
        with open(bindings.expand(context_file_name), 'w') as cf :
            toml.dump(context, cf)

        # extract the contract save files into the standard directory
        data_directory = state.get(['Contract', 'DataDirectory'], bindings['data'])

        for c in context['contexts'] :
            ic = context
            (*prefix, key) = c.split('.')
            for p in prefix :
                ic = ic[p]
            save_file = ic[key]['save_file']
            zf.extract(save_file, os.path.join(data_directory, '__contract_cache__'))

    return context

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def instantiate_notebook_from_template(contract_family_name : str, template_name : str, instance_parameters) :
    """Instantiate a new, parameterized notebook from a template

    @param contract_family_name: name of the directory where notebooks will be stored
    @param template_name : name of the template used to generate the new notebook
    @param instance_parameters : initialization parameters for the new notebook
    @return: path to the newly created notebook
    """

    notebook_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    template_file = os.path.join(notebook_directory, 'templates', template_name + '.ipynb')

    instance_identifier = ''.join(random.choices(string.ascii_letters, k=6))
    instance_directory = os.path.join(notebook_directory, 'instances', contract_family_name)
    instance_file = os.path.join(instance_directory, '{}_{}.ipynb'.format(template_name, instance_identifier))

    # the instance identifier is useful for generating instance specific
    # objects like configuration files and contexts
    instance_parameters = copy.deepcopy(instance_parameters)
    instance_parameters['instance_identifier'] = instance_identifier

    if not os.path.exists(instance_file) :
        os.makedirs(instance_directory, exist_ok=True)

        import papermill as pm
        pm.execute_notebook(
            template_file,
            instance_file,
            prepare_only=True,
            parameters=instance_parameters,
        )

    # Jupyter doesn't seem to like absolute paths in notebook to notebook
    # references; this needs more investigation. For now, just return the
    # relative path
    return os.path.relpath(instance_file)
