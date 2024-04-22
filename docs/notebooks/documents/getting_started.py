# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Getting Started
#
# This document provides an overview for preparing to work with PDO contracts through the contract
# docker container. It will walk through the necessary steps to set up a functional
# configuration. It does assume that the reader is familiar with
# [basic operation of Jupyter notebooks](https://jupytext.readthedocs.io/en/latest/).
#
# %% [markdown]
# ## How Contracts Use Jupyter
#
# Many of the PDO contract families provide Jupyter notebooks to simplify interaction with contract
# objects. Commonly, the notebooks provide a factory for instantiating a notebook for each new
# contract from one of the contract specific templates. The templates provided generally include five
# common sections:
#
# * Configure the Contract Object
# * Initialize the Jupyter Interpreter and the PDO Environment
# * Initialize the Contract Object Context
# * Operate on the Contract
# * View Contract Metadata
#
# *Configure the Contract Object*: Each notebook either loads an existing contract object from a
# file (see the PDO documentation on contract collections) or creates a new contract object based on
# an initial set of parameters. To create a new contract object, a factory will collect input that
# is used to instantiate a template notebook with the set of required parameters.
#
# *Initialize the Jupyter Interpreter and PDO Environment*: To initialize the Jupyter interpreter,
# the notebook loads the Juptyer helper module. This module imports all of the relevant PDO and
# Jupyter IPython modules to simplify code in the notebook. It also defines several procedures that
# are useful for initializing and interacting with the PDO environment.
#
# In addition, the Jupyter interpreter initialization configures an IPython extension that makes it
# easier to provide code for multiple types of operations that can be performed on the contract
# object. Specifically, the extension defines a magic keyword, `skip`, that takes a value or
# expression that, if it evaluates to True, causes the code section to be skipped during notebook
# execution.
#
# *Initialize the Contract Object Context*: The next section in the notebook creates a PDO context
# for the contract object (see the PDO documentation for more information on contexts).  The context
# includes all information necessary to create the contract object (and its dependencies) based on
# the initial set of parameters provided by the factory notebook. Beyond the initial parameters, the
# context allows for fine-grained customization of the contract object, though the defaults are
# usually sufficient.
#
# *Operate on the Contract*: The contract object may be used once it has been created and
# initialized. In general, cells in this section of the notebook are turned off by default; that is,
# `%%skip True` is added at the top of the cell. To perform an operation, change the top line to
# `%%skip False` and evaluate the cell.
#
# *View Contract Metadata*: For the curious (and those debugging contract behavior), the final
# section of most notebooks includes a section to examine the metadata associated with a contract.

# %% [markdown]
# ## Configure the PDO Environment
#
# The remainder of this notebook helps to setup and verify the PDO environment in which the
# notebooks operate. If you have started the Jupyter Lab server through the docker test interface, a
# basic environment has already been created that is sufficient for working with the notebooks.
# Otherwise, you may use the sections of this notebook to create or import signing keys for
# transactions, configure PDO services (e.g. by importing a PDO `site.toml` file), and configure
# service groups to simplify contract creation.
#
# %% [markdown]
# ## Initialize the Interpreter
#
# The following cell loads modules that configure the Jupyter interpreter and simplify interaction
# with the PDO environment.
# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

pc_jupyter.load_ipython_extension(get_ipython())

try : state
except NameError:
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# ## Create Keys
#
# PDO uses ECDSA cryptographic keys to sign transactions. Each key pair represents an identity or
# role. The list below will show a list of currently available keys. There is a form to use to
# create new keys (the refresh button will update the key list when you create new keys).
# Additional management of keys is provided by the [Key Manager Notebook](key_manager.ipynb).
#
# %%
from pdo.contracts.keys import PrivateKeyListWidget, GenerateKeyWidget

key_list = PrivateKeyListWidget(state, bindings)
key_gen = GenerateKeyWidget(state, bindings)
ip_display.display(ipywidgets.VBox([key_list, key_gen]))

# %% [markdown]
# ## Import Site Information
#
# PDO clients require information about the services that will be used for contracts. Typically, a
# service provider will create a site description file (often called `site.toml`) that can be used
# to import information about a number of services.
#
# The widget below contains information about the currently created service groups and a form
# for uploading a new site file. Additional management of service information is provided by the
# [Service Manager Notebook](service_manager.ipynb)
#
# %%
from pdo.contracts.services import ServiceListWidget
from pdo.contracts.services import ServiceUploadWidget
from pdo.contracts.services import service_labels

children = map(lambda stype : ServiceListWidget(state, bindings, stype), service_labels.keys())
service_list = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(ipywidgets.VBox([service_list, ServiceUploadWidget(state, bindings)]))

# %% [markdown]
# ## Create Service Groups
#
# Service groups are a shortcut for configuration of collections of enclave, storage, and
# provisioning services used to create and provision a PDO contract object. Each type of
# service will have its own service groups. PDO requires that each type of service have a
# service group named "default" that will be used when no groups have been specified.
#
# The widget below contains a list of service groups for each type of service and a widget for
# creating new services of each type. If there is no default service group, please create one.
#
# Additional management of service group information is provided by the [Service Groups Manager
# Notebook](service_groups_manager.ipynb)
# %%
from pdo.contracts.groups import ServiceGroupListWidget
from pdo.contracts.groups import EnclaveServiceGroupCreateWidget
from pdo.contracts.groups import ProvisioningServiceGroupCreateWidget
from pdo.contracts.groups import StorageServiceGroupCreateWidget

children = map(lambda stype : ServiceGroupListWidget(state, bindings, stype), service_labels.keys())
ip_display.display(ipywidgets.Tab(children=list(children), titles=list(service_labels.values())))

children = [
    EnclaveServiceGroupCreateWidget(state, bindings),
    ProvisioningServiceGroupCreateWidget(state, bindings),
    StorageServiceGroupCreateWidget(state, bindings),
]

titles = ['Enclave Services', 'Provisioning Services', 'Storage Services']
ip_display.display(ipywidgets.Tab(children=children, titles=titles))
