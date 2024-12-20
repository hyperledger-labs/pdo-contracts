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
# # Counter Factory
#
# This notebook simplifies the creation of counter.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_contract_families(exchange='ex', example='example')
pc_jupyter.load_ipython_extension(get_ipython())

try : state
except NameError:
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# ## Configure Counter Information
#

# %% tags=["parameters"]
counter_name = input('Name of the counter: ')
identity = input('Identity to use to create the counter [user1]: ') or "user1"
service_group = input('Service group [default]: ') or "default"

# %%
instance_parameters = {
    'counter_owner' : identity,
    'counter_name' : counter_name,
    'service_group' : service_group,
}

instance_file = pc_jupyter.instantiate_notebook_from_template(counter_name, 'counter', instance_parameters)
ip_display.display(ip_display.Markdown('[Newly created counter]({})'.format(instance_file)))
