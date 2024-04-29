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
# # Wallet Notebook
# *WORK IN PROGRESS*
#
# This notebook is used to manage the assets issued to an indivdual by an issuer contract. The
# notebook assumes that the asset type, vetting, and issuer contract objects have been created.

# %% [markdown] editable=true slideshow={"slide_type": ""}
# <hr style="border:2px solid gray">
#
# ## Configure Asset Information
#
# This section enables customization wallet. Edit the variables in the section below as necessary.
# * wallet_owner : the identity of the wallet owner
# * asset_name : the name of the asset type to be managed
# * context_file : the name of the context file where asset information is located
#

# %% tags=["parameters"]
wallet_owner = 'user1'
asset_name = 'asset'
context_file = '${etc}/${asset_name}_context.toml'
instance_identifier = ''

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ### Initialize the PDO Environment
#
# Initialize the PDO environment. This assumes that a functional PDO configuration is in place and
# that the PDO virtual environment has been activated. In particular, ensure that the groups file
# and eservice database have been configured correctly.  If you do not have a service groups
# configuration, you can set it up with the
# [service groups manager](/documents/service_groups_manager.ipynb) page
# %%
try : state
except NameError:
    common_bindings = {
        'wallet_owner' : wallet_owner,
        'asset_name' : asset_name,
    }

    (state, bindings) = pc_jupyter.initialize_environment(wallet_owner, **common_bindings)

print('environment initialized')

# %% [markdown]
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract objects that interact
# with one another. By default, the context file used in this notebook is specific to the asset
# class. We need the class to ensure that all of the information necessary for the asset itself is
# available. If you prefer to use a common context file, edit the context_file variable below.
#
# For the most part, no other modifications should be required.

# %%
context_file = bindings.expand(context_file)
print('using context file {}'.format(context_file))

# Customize the context with the user's identity
context_bindings = {
    'identity' : wallet_owner,
}

asset_path = 'asset.' + asset_name
context = pc_jupyter.ex_jupyter.initialize_asset_context(
    state, bindings, context_file, asset_path, **context_bindings)
print('context initialized')

# %% [markdown]
# ### Configure the Contract Objects
#
# Set up the connections to each of the contract objects. Although most interactions
# are with the issuer contract object, it may be necessary to verify the authority
# of the other contracts as well.

# %%
issuer_context = pc_jupyter.pbuilder.Context(state, asset_path + '.issuer')
issuer_save_file = issuer_context.get('save_file')
print('issuer contract in {}'.format(issuer_save_file))

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Issuer Contract
#
# This section defines several functions that can be used to interact with the issuer contract:
# * get_balance -- get the current number of assets associated with the given identity
# * transfer -- transfer assets from one identity to another

# %%
def get_balance(owner) :
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_get_balance, state, issuer_context, identity=wallet_owner)

def transfer(count, new_owner, old_owner=identity) :
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_transfer_assets, state, issuer_context,
        new_owner=new_owner, count=count, identity=old_owner)
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_get_balance, state, issuer_context, identity=old_owner)


# %% [markdown]
# ### Account Balance
# %%
# %%skip True
get_balance(wallet_owner)

# %% [markdown]
# ### Transfer Assets
# %%
# %%skip True
count = int(input('number of assets to transfer'))
recipient = input('identity of the recipient of the transfer')

transfer(count, recipient, wallet_owner)
