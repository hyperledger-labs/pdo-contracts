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
# # Service Management for PDO Contracts (WIP)
#
# This notebook helps to manage the services database.

# %%
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

from pdo.contracts.services import ServiceUploadWidget, ServiceSelectionWidget, ServiceListWidget
from pdo.contracts.services import service_labels, get_by_url, update_service

pc_jupyter.load_ipython_extension(get_ipython())

try :
    state
except NameError :
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# ## Import Services
#
# Typically, a site will generate a file with information about the service endpoints. The file is
# usually called `site.toml`. Upload a `site.toml` file to import services.
# %%
ip_display.display(ServiceUploadWidget(state, bindings))

# %% [markdown]
# ## Services List
#
# Display a list of the currently registered services. Services can be imported
# from a site configuration file below.
# %%
children = map(lambda stype : ServiceListWidget(state, bindings, stype), service_labels.keys())
service_list_widget = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(service_list_widget)

# %% [markdown]
# ## Verify Services
#
# Verification checks that the service exists and that its identity has not
# changed since it was added to the service database. While correct operation
# does not require service verification, it is often useful to check on the
# status of services.
# %%
def verify_service(service_type, urls, output) :
    for u in urls :
        info = get_by_url(u, service_type)
        info.verify()
        update_service(info, info)
    with output : print("Verified: {}".format(", ".join(urls)))

def create_tab(service_type) :
    return ServiceSelectionWidget(state, bindings, service_type, button_label="Verify", button_callback=verify_service)

children = map(lambda service_type : create_tab(service_type), service_labels.keys())
service_list_widget = ipywidgets.Tab(children=list(children), titles=list(service_labels.values()))
ip_display.display(service_list_widget)
