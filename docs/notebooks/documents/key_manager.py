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
# ## WORK IN PROGRESS
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
# ## List of Available Keys
#
# The following keys are available for use in PDO contracts applications.
#
# %% [markdown]
# ### Public Keys
# %%
public_key_list_widget = pc_jupyter.keys.PublicKeyListWidget(state, bindings)
ip_display.display(public_key_list_widget)

# %% [markdown]
# ### Private Keys
# %%
private_key_list_widget = pc_jupyter.keys.PrivateKeyListWidget(state, bindings)
ip_display.display(private_key_list_widget)

# %% [markdown]
# ## Create a New Key
#
# Create a new private/public key pair.
#
# %%
key_gen_widget = pc_jupyter.keys.GenerateKeyWidget(state, bindings)
ip_display.display(key_gen_widget)

# %% [markdown]
# ## Upload Keys
#
# Upload a key.
# %%
key_upload_widget = pc_jupyter.keys.UploadKeyWidget(state, bindings)
ip_display.display(key_upload_widget)
