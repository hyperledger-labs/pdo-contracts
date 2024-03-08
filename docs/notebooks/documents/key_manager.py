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
# # Key Management for PDO Contracts
#
# This notebook helps to manage keys for signing PDO contract transactions.

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
# ## Key Management

# %%
public_key_widget = pc_jupyter.keys.create_public_key_selection_widget(state,bindings)
private_key_widget = pc_jupyter.keys.create_private_key_selection_widget(state,bindings)
key_gen_widget = pc_jupyter.keys.create_generate_key_widget(state, bindings)

ip_display.display(ipywidgets.VBox([public_key_widget, private_key_widget, key_gen_widget]))

# %% [markdown]
# ## List of Available Keys

# %%
public_key_list_widget = pc_jupyter.keys.create_public_key_list_widget(state,bindings)
ip_display.display(public_key_list_widget)

private_key_list_widget = pc_jupyter.keys.create_private_key_list_widget(state,bindings)
ip_display.display(private_key_list_widget)
