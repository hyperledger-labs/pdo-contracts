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
# # Wallet Factory
#
# Use this notebook to create a wallet associated with a particular issuer.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_contract_families(exchange='ex')
pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ## Configure Wallet and Issuer Information
#
# This section enables customization of the wallet and the issuer with which it is associated.
#
# * identity : the identity of the token creator
# * asset_name : the name of tokens that will be generated
# * asset_import_file : the name of the contract collections file for the asset
#
# Note that the notebook assumes that there is a key file for the identity of the form:
# `${keys}/${identity}_private.pem`.

# %%
wallet_owner = input('Identity of the wallet owner: ')
wallet_name = input('Name of the wallet: ')

# %% [markdown]
# ## Create the Wallet Notebook
#
# Create a new wallet notebook with the specific asset identified.

# %%
instance_parameters = {
    'wallet_owner' : wallet_owner,
    'wallet_name' : wallet_name,
    'context_file' : '${etc}/${wallet_name}_context.toml',
}

instance_file = pc_jupyter.instantiate_notebook_from_template(wallet_name, 'wallet', instance_parameters)
ip_display.display(ip_display.Markdown('[Wallet]({})'.format(instance_file)))
# %%
