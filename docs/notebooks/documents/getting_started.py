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
# docker container. It will walk through the necessary steps to set up a functional configuration.
#
# %% [markdown]
# ## How Contracts Use Jupyter
#
# Many of the PDO contract families provide Jupyter notebooks to simplify interaction with contract
# objects. Commonly, the notebooks provide a factory for instantiating a notebook for each new
# contract from one of the contract specific templates.The templates provided generally share five
# common sections:
#
# * Configure the Contract Object
# * Initialize the Interpreter and the PDO Environment
# * Initialize the Contract Object Context
# * Operate on the Contract
# * View Contract Metadata
#
# To initialize the interpreter, the notebook loads the Juptyer helper module. This module imports
# all of the relevant PDO and Jupyter modules to simplify access for code in the notebook. It also
# defines several procedures that are useful for initializing and interacting with the environment.
#
# In addition, the interpreter initialization configures an IPython extension that makes it easier
# to provide code for multiple types of operations that can be performed on the contract
# object. Specifically, the extension defines a magic keyword, `skip`, that takes a value or
# expression that, if it evaluates to True, causes the code section to be skipped during notebook
# execution.
#
# The next section in the notebook configures information about the contract object associated with
# the notebook. In some cases, the variables will set by the notebook using the Papermill
# extensions. In some cases, the variables may be customized for the specific behavior desired.
#
# The following section initializes the PDO environment from the PDO configuration files. There may
# be opportunities for customization, but so long as the PDO configuration is complete changes to
# this section should be infrequent.
#
# The final common section initializes the contract context. Where the PDO initialization handles
# configuration of the PDO modules, this section handles configuration of the specific contract
# object and its relationship to other contract objects.
#
# %% [markdown]
# ## Initialize the Environment
#
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
