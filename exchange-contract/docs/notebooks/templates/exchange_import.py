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
# # Exchange Import Notebook
#
# This notebook is used to interact with an exchange contract object.

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Configure Exchange Information
#
# This section enables customization. Edit the variables in the section below as necessary.
# * identity : the identity of the creator of the asset type
# * exchange_import_file : the name of the contract import file for an existing exchange
# * exchange_context_file : the name of the context file to use for the exchange contract
#
# Note that the notebook assumes that there is a key file for the identity of the form
#
# ```bash
# ${keys}/${identity}_private.pem
# ```

# %% tags=["parameters"]
identity = 'user'
exchange_import_file = '${data}/exchange_${instance}.zip'
exchange_context_file = '${etc}/context/exchange_${instance}.toml'
instance_identifier = ''

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize the Exchange Contract

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_contract_families(exchange='ex')
pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ### Initialize the PDO Environment
#
# Initialize the PDO environment. This assumes that a functional PDO configuration is in place and
# that the PDO virtual environment has been activated. In particular, ensure that the groups file
# and eservice database have been configured correctly.  If you do not have a service groups
# configuration, you can set it up with the
# [service groups manager](/documents/service_groups_manager.ipynb) page.
#
# For the most part, no modifications should be required below.

# %%
common_bindings = {
    'instance' : instance_identifier,
}

(state, bindings) = pc_jupyter.initialize_environment(identity, **common_bindings)
print('environment initialized')

exchange_context_file = bindings.expand(exchange_context_file)
print('exchange context stored in {}'.format(exchange_context_file))

# %% [markdown]
# ### Import the Exchange Contract
#
# If you received the exchange contract as a contract export file, import it into your
# local configuration here. Adjust the name of the file to reflect where the
# contract export file is located.

# %%
if not os.path.exists(exchange_context_file) :
    pc_jupyter.import_context_file(state, bindings, exchange_context_file, exchange_import_file)

# %%
context_bindings = {
    'identity' : identity,
    'order.identity' : identity,
    'request.asset_type.identity' : identity,
    'request.vetting.identity' : identity,
    'request.issuer.identity' : identity,
    'offer.asset_type.identity' : identity,
    'offer.vetting.identity' : identity,
    'offer.issuer.identity' : identity
}

context = pc_jupyter.initialize_order_context(
    state, bindings, exchange_context_file, prefix=instance_identifier, **context_bindings)

# %%
exchange_save_file = pc_jupyter.pcontract_cmd.get_contract_from_context(state, context.get_context('order'))
print('exchange contract in {}'.format(exchange_save_file))

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Work with the Exchange Contract

# %% [markdown]
# ### Examine the Offered Asset

# %%
# %%skip True
import json
session = pc_jupyter.pbuilder.SessionParameters(save_file=exchange_save_file)
offered_asset = pc_jupyter.pcontract.invoke_contract_op(
            pc_jupyter.ex_exchange.op_examine_offered_asset, state, context.get_context('order'), session)
offered_asset = json.loads(offered_asset)
ip_display.display(ip_display.JSON(offered_asset))


# %% [markdown]
# ### Examine the Requested Asset

# %%
# %%skip True
import json
session = pc_jupyter.pbuilder.SessionParameters(save_file=exchange_save_file)
offered_asset = pc_jupyter.pcontract.invoke_contract_op(
            pc_jupyter.ex_exchange.op_examine_requested_asset, state, context.get_context('order'), session)
offered_asset = json.loads(offered_asset)
ip_display.display(ip_display.JSON(offered_asset))


# %% [markdown]
# ### Match the Order

# %%

# %% [markdown]
# ### Cancel Order

# %%

# %% [markdown]
# ### Claim Offered Asset

# %%

# %% [markdown]
# ### Claim Requested Asset

# %%

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Contract Metadata

# %% [markdown]
# ### Export Contract File
#
# To share a contract with others, they need the client plugin modules, the context of the contract family (which describes the relationship between the contract objects), and the contract save files (which provides information about the configuration of the contract objects). Plugins are generally distributed separately (they are applicable to many contract objects). The context and contract save files can be packed into a single bundle that can easily be shared.
#
# In the code block below, you will likely want to change the value of the export path to the directory where the contract family export file will be saved. Feel free to change the file name as well. The default uses the asset name.

# %%
# %%skip True
export_file = '${data}/exchange_${instance}.zip'
contexts = [
    'offer.asset_type', 'offer.vetting', 'offer.issuer',
    'request.asset_type', 'request.vetting', 'request.issuer',
    'order'
]
pc_jupyter.export_context_file(state, bindings, context, contexts, export_file)

# %% [markdown]
# ### Contract Save Files
#
# This notebook contains one contract file. Detailed information can be found below.

# %%
# %%skip True
ip_display.display(ip_display.JSON(filename=exchange_save_file))

# %% [markdown]
# ### Contract Context

# %%
# %%skip True
ip_display.display(context.context)
