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
# # Service Groups Management for PDO Contracts
#
# This notebook helps to manage the services database.

# %%
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

from pdo.contracts.services import service_labels
from pdo.contracts.groups import ServiceGroupListWidget
from pdo.contracts.groups import EnclaveServiceGroupCreateWidget
from pdo.contracts.groups import ProvisioningServiceGroupCreateWidget
from pdo.contracts.groups import StorageServiceGroupCreateWidget

pc_jupyter.load_ipython_extension(get_ipython())

try :
    state
except NameError:
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# ## List of Available Service Groups
#
# %%
children = map(lambda stype : ServiceGroupListWidget(state, bindings, stype), service_labels.keys())
service_list_widget = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(service_list_widget)

# %% [markdown]
# ## Create a New Enclave Service Group
#
# %%
ip_display.display(EnclaveServiceGroupCreateWidget(state, bindings))

# %% [markdown]
# ## Create a New Provisioning Service Group
#
# %%
ip_display.display(ProvisioningServiceGroupCreateWidget(state, bindings))

# %% [markdown]
# ## Create a New Storage Service Group
#
# %%
ip_display.display(StorageServiceGroupCreateWidget(state, bindings))
