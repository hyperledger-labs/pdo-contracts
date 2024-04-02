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
# # Create a New Exchange Contract
#
# This notebook is used to interact with an exchange contract object. The assumption is that you have imported the issuer contracts that will be involved in the exchange.

# %% [markdown] editable=true papermill={} slideshow={"slide_type": ""}
# <hr style="border:2px solid gray">
#
# ## Configure Exchange Information
#
# This section enables customization wallet. Edit the variables in the section below as necessary.
# * identity : the identity of the creator of the asset type
# * offer_context_file : the name of the context file with information about the offered asset
# * offer_count : number of assets to offer
# * request_context_file : the name of the context file with information about the requested asset
# * request_count : number of assets to request
#
# Note that the notebook assumes that there is a key file for the identity of the form
#
# ```bash
# ${keys}/${identity}_private.pem
# ```

# %% tags=["parameters"]
identity = 'user'
offer_context_file = '${etc}/context/offer_issuer.toml'
offer_count = 1
request_context_file = '${etc}/context/request_issuer.toml'
request_count = 1
exchange_context_file = '${etc}/context/exchange_${instance}.toml'
instance_identifier = ''
service_host = 'localhost'

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize the Exchange Contract

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
# In the next box we will set up the PDO client configuration. This will load any client
# configuration files, service group files, and service database files. Common bindings provides a
# means to override specific configuration variables and set variable expansion values.
#
# For the most part, no modifications should be required.

# %%
common_bindings = {
    'host' : service_host,
    'service_host' : service_host,
    'instance' : instance_identifier,
}

(state, bindings) = pc_jupyter.initialize_environment(identity, **common_bindings)

offer_context_file = bindings.expand(offer_context_file)
request_context_file = bindings.expand(request_context_file)
exchange_context_file = bindings.expand(exchange_context_file)

print('environment initialized')

# %% [markdown]
# ### Import the Issuer Contracts
#
# The exchange notebook assumes that issuer contracts have been fully imported and the context files are available. If you received the issuer contracts as contract export files, import them into your local configuration. Adjust the name of the file to reflect where the contract export files are located.

# %%
# %%skip True
import_file = input('Name of the import file for the offer issuer contract')
pc_jupyter.import_context_file(state, bindings, offer_context_file, import_file)

# %%
# %%skip True
import_file = input('Name of the import file for the request issuer contract')
pc_jupyter.import_context_file(state, bindings, request_context_file, import_file)

# %% [markdown]
# ### Create the Exchange Contract Context
#
# Create a new exchange contract context. The contract context defines the configuration for a collection of contract objects that interact with one another. By default, the context file used in this notebook is specific to the exchange contract object that will be created. If you prefer to use a common context file, edit the context_file variable below.

# %% [markdown]
# #### Import the Asset Issuer Contexts
#
# The context files for the assets used for the offer and request must be available. The file names for these context files should have been set above. The context for each of the issuers will be loaded with the exchange instance identifier prefix.

# %%
pc_jupyter.pcontext.Context.LoadContextFile(
    state, bindings, offer_context_file, prefix='{}.offer'.format(instance_identifier))

pc_jupyter.pcontext.Context.LoadContextFile(
    state, bindings, request_context_file, prefix='{}.request'.format(instance_identifier))

# %% [markdown]
# #### Create the Exchange Context
#
# Create the context for the exchange contract. In addition, we need to ensure that the identity used to interact with the issuer contracts is the same as the identity used for the exchange contract. For the most part, all settings should have been set above.

# %%
context_bindings = {
    'identity' : identity,
    'order.identity' : identity,
    'order.offer.count' : offer_count,
    'order.request.count' : request_count,
    'request.asset_type.identity' : identity,
    'request.vetting.identity' : identity,
    'request.issuer.identity' : identity,
    'offer.asset_type.identity' : identity,
    'offer.vetting.identity' : identity,
    'offer.issuer.identity' : identity
}

context = pc_jupyter.ex_jupyter.initialize_order_context(
    state, bindings, exchange_context_file, prefix=instance_identifier, **context_bindings)

# %% [markdown]
# ### Create the Exchange Contract
#
# We are now ready to create the exchange contract. If the exchange contract save file already exists (implying that the contract already exists), then skip this step.

# %%
exchange_save_file = pc_jupyter.pcontract_cmd.get_contract_from_context(state, context.get_context('order'))
if exchange_save_file is None :
    exchange_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_exchange.cmd_create_order, state, context.get_context('order'))
    pc_jupyter.pbuilder.Context.SaveContextFile(state, exchange_context_file, prefix=instance_identifier)
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
contract_identifier = 'exchange_{}'.format(instance_identifier)
contexts = [
    'offer.asset_type', 'offer.vetting', 'offer.issuer',
    'request.asset_type', 'request.vetting', 'request.issuer',
    'order'
]
contract_files = {
    'order' : exchange_save_file
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
