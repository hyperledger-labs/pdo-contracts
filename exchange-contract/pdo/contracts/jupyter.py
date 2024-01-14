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
import importlib.util
import logging
import os
import random
import string
import sys
import types
import typing

from zipfile import ZipFile

import IPython.display as ip_display

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.context as pcontext
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell

import pdo.client.commands.context as pcontext_cmd
import pdo.client.commands.contract as pcontract_cmd
import pdo.client.commands.collection as pcollection_cmd

import pdo.contracts.keys as keys

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
# the module assumes the PDO_JUPYTER_ROOT is set and that it points to
# a directory that exists in the file system; this is checked on
# module load with an import exception thrown if there is an error
# -----------------------------------------------------------------
notebook_root = os.environ.get('PDO_JUPYTER_ROOT')

if notebook_root is None :
    raise ImportError('PDO_JUPYTER_ROOT environment variable must be set')

notebook_root = os.path.abspath(notebook_root)

if not os.path.exists(notebook_root) :
    raise ImportError('Notebook root directory {} does not exist'.format(notebook_root))

notebook_instance_root = os.path.join(notebook_root, 'instances')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def find_contract_family(current_path) :
    """Find the contract family root directory

    Assuming that the current path is somewhere in the contract family directory
    hiearchy, find the root path.
    """
    assert current_path.startswith(notebook_root)

    family = None
    while current_path != notebook_root and current_path != notebook_instance_root :
        (current_path, family) = os.path.split(current_path)

    return family

def contract_family_root(family) :
    """Contract family root: <notebook_root>/<family>
    """
    return os.path.join(os.path.join(notebook_root, family))

def contract_family_template_root(family) :
    """Contract family template root: <notebook_root>/<family>/templates
    """
    return os.path.join(contract_family_root(family), 'templates')

def contract_family_instance_root(family) :
    """Contract family instance root: <notebook_root>/instances/<family>
    """
    return os.path.join(notebook_instance_root, family)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def instantiate_notebook_from_template(contract_collection_name : str, template_name : str, instance_parameters) -> str :
    """Instantiate a new, parameterized notebook from a template

    @param contract_collection_name: name of the directory where notebooks will be stored
    @param template_name : name of the template used to generate the new notebook
    @param instance_parameters : initialization parameters for the new notebook
    @return: path to the newly created notebook
    """

    family = find_contract_family(os.getcwd())
    template_file = os.path.join(contract_family_template_root(family), template_name + '.ipynb')

    # The file created has the following structure:
    #   <notebook_root>/instances/<family>/<collection>/<template>_<uid>.ipynb"
    instance_directory = os.path.join(contract_family_instance_root(family), contract_collection_name)
    instance_identifier = ''.join(random.choices(string.ascii_letters, k=6))
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

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def export_contract_collection(
    state : pbuilder.state.State,
    bindings : pbuilder.bindings.Bindings,
    context : pbuilder.context.Context,
    paths : typing.List[str],
    identifier : str) :
    """Create a contract collection file in the notebook download directory
    """

    data_directory = bindings.get('data', state.get(['Contract', 'DataDirectory']))
    contract_cache = bindings.get('save', os.path.join(data_directory, '__contract_cache__'))
    export_file = '{}.zip'.format(identifier)

    pcollection_cmd.export_contract_collection(context, paths, contract_cache, export_file)
    return export_file

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def create_download_link(filename : str, label : str = 'Download File') :
    """Create HTML display that will download a file"""
    content = '<a href={} download>{}</a>'.format(filename, label)
    return ip_display.HTML(content)

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
    except :
        pass

    # load the plugins module for the contract family, this
    # should provide a list of all the plugins in the family
    # (in the __all__ variable)
    try :
        family_name = 'pdo.{}.plugins'.format(cf)
        family_module = importlib.import_module(family_name)

        for plugin_name in family_module.__all__ :
            plugin_module = importlib.import_module('{}.{}'.format(family_name, plugin_name))
            globals()['{}_{}'.format(cs,plugin_name)] = plugin_module
    except :
        pass
