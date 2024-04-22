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
# *WORK IN PROGRESS*
# # Wallet Notebook
#
# This notebook is used to manage the assets issued to an indivdual by an issuer contract. The
# notebook assumes that the asset type, vetting, and issuer contract objects have been created.

# %% [markdown] editable=true slideshow={"slide_type": ""}
# <hr style="border:2px solid gray">
#
# ## Configure Issuer Information
#
# This section enables customization wallet. Edit the variables in the section below as necessary.
# * identity : the identity of the creator of the asset type
# * asset_name : the name of the asset type to be created
# * context_file : the name of the context file where token information is located
#
# When this notebook is instantiated, it will generally provide default values for `identity`,
# `asset_name`, `context_file` and `notebook_directory`.
#
# Note that the notebook assumes that there is a key file for the identity of the form
#
# ```bash
# ${keys}/${identity}_private.pem
# ```

# %% tags=["parameters"]
identity = 'user'
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
common_bindings = {
}

(state, bindings) = pc_jupyter.initialize_environment(identity, **common_bindings)
print('environment initialized')

# %% [markdown]
# ### Import the Contract
#
# If you received the contract as a contract export file, import it into your
# local configuration here. Adjust the name of the file to reflect where the
# contract export file is located.

# %%
# %%skip True
import_file = '${{data}}/{}.zip'.format(asset_name)
pc_jupyter.import_context(state, bindings, context_file, import_file)

# %% [markdown]
# ### Import the Context
#
# The contract context defines the configuration for a collection of contract objects that interact
# with one another. By default, the context file used in this notebook is specific to the asset
# class. We need the class to ensure that all of the information necessary for the asset itself is
# available. If you prefer to use a common context file, edit the context_file variable below.
#
# For the most part, no other modifications should be required.

# %%
asset_path = 'asset.' + asset_name
context_file = bindings.expand(context_file)
print('using context file {}'.format(context_file))

# Customize the context with the user's identity
context_bindings = {
    'asset_type.identity' : identity,
    'vetting.identity' : identity,
    'issuer.identity' : identity,
}

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
asset_type_context = pc_jupyter.pbuilder.Context(state, asset_path + '.asset_type')
asset_type_save_file = asset_type_context.get('save_file')
print('asset type contract in {}'.format(asset_type_save_file))

vetting_context = pc_jupyter.pbuilder.Context(state, asset_path + '.vetting')
vetting_save_file = vetting_context.get('save_file')
print('vetting contract in {}'.format(vetting_save_file))

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
        pc_jupyter.ex_issuer.cmd_get_balance, state, issuer_context, identity=owner)

def transfer(count, new_owner, old_owner=identity) :
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_transfer_assets, state, issuer_context,
        new_owner=new_owner, count=count, identity=old_owner)
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_get_balance, state, issuer_context, identity=old_owner)


# %% [markdown]
# ### Get the Account Balance

# %%
# %%skip True
owner = input('identity to check [{}]'.format(identity)) or identity
get_balance(owner)

# %% [markdown]
# ### Transfer Assets

# %%
# %%skip True
count = int(input('number of assets to transfer'))
new_owner = input('identity of the recipient of the transfer')
old_owner = input('identity of the source of the transfer [{}]'.format(identity)) or identity

transfer(count, new_owner, old_owner)

# %% [markdown] editable=true slideshow={"slide_type": ""}
# ### Escrow Assets
#
# Work in Progress

# %%
