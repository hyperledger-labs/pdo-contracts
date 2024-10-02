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
# # Managing the PDO Environment
#
# This notebook provides an aggregate interface for preparing to work with PDO contracts and
# describes the necessary steps to set up a functional configuration. It assumes that the reader is
# familiar with [basic operation of Jupyter notebooks](https://jupytext.readthedocs.io/en/latest/).
#
# This notebook helps to setup and verify the PDO environment in which the notebooks operate. If you
# have started the Jupyter Lab server through the PDO contracts docker test interface, a basic
# environment has already been created that is sufficient for working with the notebooks.
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
from pdo.contracts.jupyter.keys import PrivateKeyListWidget
from pdo.contracts.jupyter.keys import PublicKeyListWidget
from pdo.contracts.jupyter.keys import GenerateKeyWidget
from pdo.contracts.jupyter.keys import UploadKeyWidget

private_key_list = PrivateKeyListWidget(state, bindings)
public_key_list = PublicKeyListWidget(state, bindings)
key_generate = GenerateKeyWidget(state, bindings)
key_import = UploadKeyWidget(state, bindings)

children = [public_key_list, private_key_list, key_generate, key_import]
titles = ['Public Key List', 'Private Key List', 'Generate Key Pair', 'Import Keys']
ip_display.display(ipywidgets.Tab(children=children, titles=titles))
# %% [markdown]
# ## Import Site Information
#
# PDO clients require information about the services that will be used for contracts. Typically, a
# service provider will create a site description file (often called `site.toml`) that can be used
# to import information about services offered by a site.
#
# The widget below contains information about the currently created service groups and a form
# for uploading a new site file. Additional management of service information is provided by the
# [Service Manager Notebook](service_manager.ipynb)
#
# %%
from pdo.contracts.jupyter.services import ServiceListWidget
from pdo.contracts.jupyter.services import ServiceUploadWidget
from pdo.contracts.jupyter.services import service_labels

children = map(lambda stype : ServiceListWidget(state, bindings, stype), service_labels.keys())
titles = service_labels.values()
service_list = ipywidgets.Tab(children=list(children), titles=list(titles))
ip_display.display(ipywidgets.VBox([service_list, ServiceUploadWidget(state, bindings)]))

# %% [markdown]
# ## Service Groups
#
# Service groups are a shortcut for configuration of collections of enclave, storage, and
# provisioning services used to create and provision a PDO contract object. Each type of
# service will have its own service groups. PDO requires that each type of service have a
# service group named "default" that will be used when no groups have been specified.
#
# Additional management of service group information is provided by the [Service Groups Manager
# Notebook](service_groups_manager.ipynb)
# %%
from pdo.contracts.jupyter.groups import ServiceGroupListWidget
from pdo.contracts.jupyter.groups import EnclaveServiceGroupCreateWidget
from pdo.contracts.jupyter.groups import ProvisioningServiceGroupCreateWidget
from pdo.contracts.jupyter.groups import StorageServiceGroupCreateWidget
# %% [markdown]
# ### List Service Groups
#
# The widget below contains a list of service groups for each type of service.
# %%
children = map(lambda stype : ServiceGroupListWidget(state, bindings, stype), service_labels.keys())
titles = service_labels.values()
ip_display.display(ipywidgets.Tab(children=list(children), titles=list(titles)))

# %% [markdown]
# ### Create Service Groups
#
# The widget below enables creation of new service groups of each type. If there is no default
# service group, please create one.
# %%
children = [
    EnclaveServiceGroupCreateWidget(state, bindings),
    ProvisioningServiceGroupCreateWidget(state, bindings),
    StorageServiceGroupCreateWidget(state, bindings),
]

titles = ['Enclave Services', 'Provisioning Services', 'Storage Services']
ip_display.display(ipywidgets.Tab(children=children, titles=titles))
