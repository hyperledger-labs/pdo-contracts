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
# # Issuer Notebook
#
# This notebook assumes that the asset type, vetting, and issuer contract objects are all created by
# the same identity.

# %% [markdown]
# ## Configure Issuer Information
#
# This section enables customization of the token. Edit the variables in the section below as necessary.
# * identity : the identity of the creator of the asset type
# * asset_name : the name of the asset type to be created
# * asset_description : a description of the asset
# * asset_link : URL for more detailed information about the asset type
# * context_file : the name of the context file where token information is located
# * service_host : default host where the contract objects will be created
#
# When this notebook is instantiated, it will generally provide default values for `identity`,
# `asset_name`, `service_host`, and `notebook_directory`.
#
# Note that the notebook assumes that there is a key file for the identity of the form
#
# ```bash
# ${keys}/${identity}_private.pem
# ```
#

# %% tags=["parameters"]
identity = 'user'
asset_name = 'asset'
asset_description = 'this is an asset'
asset_link = 'http://'
context_file = '${etc}/context/${asset_name}_${instance}.toml'
instance_identifier = ''
service_host = 'localhost'

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
# and eservice database have been configured correctly.
#
# For the most part, no modifications should be required below.
# %%
common_bindings = {
    'host' : service_host,
    'service_host' : service_host,
    'asset_name' : asset_name,
    'instance' : instance_identifier,
}

(state, bindings) = pc_jupyter.initialize_environment(identity, **common_bindings)
print('environment initialized')

# %% [markdown]
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract objects that interact
# with one another. By default, the context file used in this notebook is specific to th eassee
# clasn. We need the class to ensure that all of the information necessary for th eassen itself is
# availaben. If you prefer to use a common context file, edit the context_file variable below.
#
# For the most part, no other modifications should be required.

# %%
asset_path = 'asset.' + asset_name
context_file = bindings.expand(context_file)
print("using context file {}".format(context_file))

context_bindings = {
    'asset_type.identity' : identity,
    'asset_type.name' : asset_name,
    'asset_type.description' : asset_description,
    'asset_type.link' : asset_link,
    'vetting.identity' : identity,
    'issuer.identity' : identity,
}
context = pc_jupyter.ex_jupyter.initialize_asset_context(
    state, bindings, context_file, asset_path, **context_bindings)
print('context initialized')

# %% [markdown]
# ### Create the Contracts

# %%
asset_type_context = pc_jupyter.pbuilder.Context(state, asset_path + '.asset_type')
asset_type_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ex_asset_type.cmd_create_asset_type, state, asset_type_context)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=asset_path)
print('asset type contract in {}'.format(asset_type_save_file))

vetting_context = pc_jupyter.pbuilder.Context(state, asset_path + '.vetting')
vetting_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ex_vetting.cmd_create_vetting_organization, state, vetting_context)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=asset_path)
print('vetting contract in {}'.format(vetting_save_file))

issuer_context = pc_jupyter.pbuilder.Context(state, asset_path + '.issuer')
issuer_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ex_issuer.cmd_create_issuer, state, issuer_context)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=asset_path)
print('issuer contract in {}'.format(issuer_save_file))

# %% [markdown]
# ### Approve Authority Chain
#
# Once the contracts are created, we need to establish the authority relationship. All issuers must
# be vetted. In this case, since the contracts are all created by the same individual, establishing
# the authority is relatively straight forward.

# %%
pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ex_vetting.cmd_approve_issuer, state, vetting_context,
    issuer=asset_path + '.issuer')

if not issuer_context.has_key('initialized') :
    pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_issuer.cmd_initialize_issuer, state, issuer_context)

    issuer_context.set('initialized', True)
    pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=asset_path)

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Contract

# %% [markdown]
# ### Issue Assets
#
# The issue assets function can be used to issue assets to a user. There must be a public key
# available for the user in the file `${keys}/${user}_public.pem`.

# %%
def issue_assets(owner, count) :
    try :
        pc_jupyter.pcommand.invoke_contract_cmd(
            pc_jupyter.ex_issuer.cmd_issue_assets, state, issuer_context,
            owner=owner, count=count)
    except ValueError as v :
        print("assets have already been issued to {}".format(owner))

# %%
# %%skip True
issue_assets('user1', 50)

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Share Contract
#
# To share a contract with others, they need the client plugin modules,
# the context of the contract family (which describes the relationship between
# the contract objects), and the contract save files (which provides information
# about the configuration of the contract objects). Plugins are generally
# distributed separately (they are applicable to many contract objects). The
# context and contract save files can be packed into a single bundle that
# can easily be shared.
#
# In the code block below, you will likely want to change the value of the export
# path to the directory where the contract family export file will be saved. Feel
# free to change the file name as well. The default uses the asset name.

# %%
contract_identifier = '{}_{}'.format(asset_name, instance_identifier)
contexts = ['asset_type', 'vetting', 'issuer']
contract_files = {
    'asset_type' : asset_type_save_file,
    'vetting' : vetting_save_file,
    'issuer' : issuer_save_file,
}

# %%
# %%skip True
export_file = pc_jupyter.export_contract_collection(state, bindings, context, contexts, contract_identifier)
ip_display.display(pc_jupyter.create_download_link(export_file, 'Download Contract Collection File'))

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Contract Metadata
#
# The cells below provide a means inspecting information about the contract. In general
# this is useful for contract debugging.

# %% [markdown]
# ### Contract Save Files

# %% tags=["hide-input"]
# %%skip True
for k, f in contract_files.items() :
    ip_display.display(ip_display.JSON(root=k, filename=os.path.join(bindings.expand('${save}'), f)))

# %% [markdown]
# ### Contract Context

# %% tags=["hide-input"]
# %%skip True
ip_display.display(context.context)
