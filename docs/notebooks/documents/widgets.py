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
# # Sample Widgets
# ## WORK IN PROGRESS
#
# This notebook demonstrates a variety of Jupyter widgets for PDO.

# %%
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

from pdo.contracts.jupyter.services import service_labels, ServiceSelectionWidget
from pdo.contracts.jupyter.groups import ServiceGroupSelectionWidget

pc_jupyter.load_ipython_extension(get_ipython())

try :
    state
except NameError:
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# # Key Management Widgets
# %% [markdown]
# ## Key Selection Widgets
# %%
def display_key(selection, output) :
    with output :
        print("Selection: {}".format(selection))

public_key_widget = pc_jupyter.keys.PublicKeySelectionWidget(state, bindings, "Display", display_key)
ip_display.display(public_key_widget)

private_key_widget = pc_jupyter.keys.PrivateKeySelectionWidget(state, bindings, "Display", display_key)
ip_display.display(private_key_widget)

# %% [markdown]
# # Service Management Widgets
# %% [markdown]
# ## Service Selection Widget
# %%
def display_service(service_type, selection, output) :
    with output :
        print("Selection [{}]: {}".format(service_type, ", ".join(selection)))

def create_service_selection(service_type) :
    return ServiceSelectionWidget(state, bindings, service_type, 'Display', display_service)

children = map(lambda service_type : create_service_selection(service_type), service_labels.keys())
service_selection_widget = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(service_selection_widget)

# %% [markdown]
# # Service Groups Widgets
# %% [markdown]
# ## Select Service Groups
# %%
def display_group(service_type, selection, output) :
    with output :
        print("Selection [{}]: {}".format(service_type, selection))

def create_group_selection(service_type) :
    return ServiceGroupSelectionWidget(state, bindings, service_type, 'Display', display_group)

children = map(lambda service_type : create_group_selection(service_type), service_labels.keys())
group_selection_widget = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(group_selection_widget)
